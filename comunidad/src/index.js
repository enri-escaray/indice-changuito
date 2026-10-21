// Servidor de la comunidad del Índice Changuito (Cloudflare Worker + D1 + Turnstile).
//
//   POST /precios           carga un precio (sin cuenta, con captcha)
//   GET  /precios?ean=…     precios confirmados de un producto (últimos 30 días)
//   GET  /exportar.csv      todos los precios confirmados, para el robot diario
//   GET  /admin             página de moderación (pide la clave de admin)
//   GET  /admin/pendientes  · GET /admin/foto?id=… · POST /admin/moderar   (con la clave)

import { MAX_POR_DIA, aCsv, confirma, hoyEnArgentina, validarReporte } from "./reglas.js";
import { PAGINA_ADMIN } from "./admin.js";

const COLUMNAS_PUBLICAS = ["id", "fecha", "ean", "producto", "unidad", "tienda", "provincia", "localidad", "precio", "oferta", "estado"];
const MAX_CUERPO = 450_000;

const json = (datos, estado = 200, encabezados = {}) =>
  new Response(JSON.stringify(datos), { status: estado, headers: { "Content-Type": "application/json; charset=utf-8", ...encabezados } });

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const origen = request.headers.get("Origin") || "";
    const permitidos = (env.ORIGENES || "").split(",").map((s) => s.trim()).filter(Boolean);
    const corsCarga = permitidos.includes(origen) ? { "Access-Control-Allow-Origin": origen, Vary: "Origin" } : {};
    const corsLectura = { "Access-Control-Allow-Origin": "*" };

    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: { ...corsCarga, "Access-Control-Allow-Methods": "GET, POST", "Access-Control-Allow-Headers": "Content-Type", "Access-Control-Max-Age": "86400" },
      });
    }
    try {
      if (url.pathname === "/precios" && request.method === "POST") return await cargar(request, env, corsCarga);
      if (url.pathname === "/precios" && request.method === "GET") return await listar(url, env, corsLectura);
      if (url.pathname === "/exportar.csv") return await exportar(env);
      if (url.pathname === "/admin") return new Response(PAGINA_ADMIN, { headers: { "Content-Type": "text/html; charset=utf-8" } });
      if (url.pathname.startsWith("/admin/")) return await admin(request, url, env);
      return json({ error: "No existe." }, 404, corsLectura);
    } catch (error) {
      console.error(error);
      return json({ errores: ["Algo falló de nuestro lado. Probá de nuevo en un rato."] }, 500, corsCarga);
    }
  },
};

async function cargar(request, env, cors) {
  if (!cors["Access-Control-Allow-Origin"]) return json({ errores: ["Origen no permitido."] }, 403);
  if (Number(request.headers.get("Content-Length") || 0) > MAX_CUERPO) {
    return json({ errores: ["El envío es demasiado grande. Probá con una foto más chica."] }, 413, cors);
  }
  const cuerpo = await request.json().catch(() => null);
  if (!cuerpo || typeof cuerpo !== "object") return json({ errores: ["No se pudo leer el envío."] }, 400, cors);

  const ip = request.headers.get("CF-Connecting-IP") || "";
  if (!(await captchaValido(cuerpo.captcha, ip, env))) {
    return json({ errores: ["No pudimos verificar que seas una persona. Probá de nuevo."] }, 400, cors);
  }
  const { ok, errores, datos } = validarReporte(cuerpo, hoyEnArgentina());
  if (!ok) return json({ errores }, 400, cors);

  // La IP nunca se guarda: solo un hash con sal, para no contar dos veces a la misma persona.
  const ip_hash = await hashConSal(ip, env.SAL_IP || "");
  const { n } = await env.DB.prepare("SELECT COUNT(*) AS n FROM reportes WHERE ip_hash = ? AND creado >= datetime('now', '-1 day')")
    .bind(ip_hash).first();
  if (n >= MAX_POR_DIA) return json({ errores: ["Llegaste al máximo de precios por hoy. Gracias por ayudar."] }, 429, cors);

  const foto = datos.foto ? Uint8Array.from(atob(datos.foto), (c) => c.charCodeAt(0)).buffer : null;
  const { meta } = await env.DB.prepare(
    "INSERT INTO reportes (fecha, ean, producto, unidad, tienda, provincia, localidad, precio, oferta, foto, ip_hash) VALUES (?,?,?,?,?,?,?,?,?,?,?)"
  ).bind(datos.fecha, datos.ean, datos.producto, datos.unidad, datos.tienda, datos.provincia, datos.localidad, datos.precio, datos.oferta ? 1 : 0, foto, ip_hash).run();
  const id = meta.last_row_id;

  // ¿Otra persona ya vio el mismo precio? Entonces los dos quedan confirmados.
  const { results } = await env.DB.prepare(
    `SELECT id, fecha, ean, producto, unidad, tienda, provincia, precio, ip_hash FROM reportes
     WHERE id != ? AND provincia = ? AND estado IN ('pendiente', 'confirmado', 'aprobado')
       AND fecha >= date(?, '-3 days') AND (ean = ? OR (ean IS NULL AND ? IS NULL))`
  ).bind(id, datos.provincia, datos.fecha, datos.ean, datos.ean).all();
  const coincidencias = results.filter((previo) => confirma({ ...datos, ip_hash }, previo));
  let estado = "pendiente";
  if (coincidencias.length) {
    estado = "confirmado";
    const ids = [id, ...coincidencias.map((p) => p.id)];
    await env.DB.prepare(`UPDATE reportes SET estado = 'confirmado' WHERE estado = 'pendiente' AND id IN (${ids.map(() => "?").join(",")})`)
      .bind(...ids).run();
  }
  return json({ ok: true, id, estado }, 201, cors);
}

async function listar(url, env, cors) {
  const ean = (url.searchParams.get("ean") || "").replace(/\D/g, "");
  if (!ean) return json({ error: "Falta el código de barras (?ean=…)." }, 400, cors);
  const { results } = await env.DB.prepare(
    `SELECT fecha, tienda, provincia, localidad, precio, oferta, unidad, estado FROM reportes
     WHERE ean = ? AND estado IN ('confirmado', 'aprobado') AND fecha >= date('now', '-30 days')
     ORDER BY fecha DESC, id DESC LIMIT 50`
  ).bind(ean).all();
  return json({ precios: results }, 200, { ...cors, "Cache-Control": "public, max-age=300" });
}

async function exportar(env) {
  const { results } = await env.DB.prepare(
    `SELECT ${COLUMNAS_PUBLICAS.join(", ")} FROM reportes WHERE estado IN ('confirmado', 'aprobado') ORDER BY fecha, id`
  ).all();
  return new Response(aCsv(results, COLUMNAS_PUBLICAS), {
    headers: { "Content-Type": "text/csv; charset=utf-8", "Access-Control-Allow-Origin": "*" },
  });
}

async function admin(request, url, env) {
  const clave = (request.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
  if (!env.ADMIN_TOKEN || !(await mismoTexto(clave, env.ADMIN_TOKEN))) return json({ error: "Clave incorrecta." }, 401);

  if (url.pathname === "/admin/pendientes") {
    const { results } = await env.DB.prepare(
      `SELECT id, creado, fecha, ean, producto, unidad, tienda, provincia, localidad, precio, oferta, foto IS NOT NULL AS tiene_foto
       FROM reportes WHERE estado = 'pendiente' ORDER BY id DESC LIMIT 200`
    ).all();
    return json({ pendientes: results });
  }
  if (url.pathname === "/admin/foto") {
    const fila = await env.DB.prepare("SELECT foto FROM reportes WHERE id = ?").bind(Number(url.searchParams.get("id"))).first();
    if (!fila || !fila.foto) return json({ error: "Sin foto." }, 404);
    return new Response(new Uint8Array(fila.foto), { headers: { "Content-Type": "image/jpeg", "Cache-Control": "private, max-age=3600" } });
  }
  if (url.pathname === "/admin/moderar" && request.method === "POST") {
    const { id, estado } = await request.json();
    if (!["aprobado", "rechazado"].includes(estado)) return json({ error: "Estado inválido." }, 400);
    await env.DB.prepare("UPDATE reportes SET estado = ? WHERE id = ?").bind(estado, Number(id)).run();
    return json({ ok: true });
  }
  return json({ error: "No existe." }, 404);
}

async function captchaValido(token, ip, env) {
  if (!token || !env.TURNSTILE_SECRET) return false;
  const formulario = new FormData();
  formulario.append("secret", env.TURNSTILE_SECRET);
  formulario.append("response", token);
  if (ip) formulario.append("remoteip", ip);
  const respuesta = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", { method: "POST", body: formulario });
  const resultado = await respuesta.json();
  return resultado.success === true;
}

async function hashConSal(texto, sal) {
  const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(`${sal}:${texto}`));
  return [...new Uint8Array(bytes)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

// Compara dos textos sin cortar en el primer carácter distinto (evita adivinar la clave por tiempos).
async function mismoTexto(a, b) {
  const [ha, hb] = await Promise.all([hashConSal(a, "comparar"), hashConSal(b, "comparar")]);
  let diferencia = 0;
  for (let i = 0; i < ha.length; i++) diferencia |= ha.charCodeAt(i) ^ hb.charCodeAt(i);
  return diferencia === 0;
}
