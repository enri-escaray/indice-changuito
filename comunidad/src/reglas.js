// Reglas de la carga de precios de la comunidad: validación, confirmación y exportación.
// No dependen de Cloudflare, así se prueban con `node --test`.

export const PROVINCIAS = [
  "Ciudad de Buenos Aires", "Buenos Aires", "Catamarca", "Chaco", "Chubut", "Córdoba", "Corrientes",
  "Entre Ríos", "Formosa", "Jujuy", "La Pampa", "La Rioja", "Mendoza", "Misiones", "Neuquén",
  "Río Negro", "Salta", "San Juan", "San Luis", "Santa Cruz", "Santa Fe", "Santiago del Estero",
  "Tierra del Fuego", "Tucumán",
];
export const UNIDADES = ["unidad", "kg", "litro"];
export const MAX_FOTO_BYTES = 300 * 1024;
export const MAX_POR_DIA = 30;
// Dos reportes se confirman entre sí si son de personas distintas, del mismo producto, súper,
// provincia y unidad, con hasta 3 días y 5 % de diferencia.
export const DIAS_PARA_CONFIRMAR = 3;
export const DIFERENCIA_PARA_CONFIRMAR = 0.05;

const texto = (valor) => (typeof valor === "string" ? valor.trim().replace(/\s+/g, " ") : "");
const sinTildes = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

export function diasEntre(desde, hasta) {
  return Math.round((Date.parse(hasta) - Date.parse(desde)) / 864e5);
}

/** Dígito verificador GTIN (EAN-8, UPC-12, EAN-13). */
export function eanValido(ean) {
  if (!/^(\d{8}|\d{12}|\d{13})$/.test(ean)) return false;
  const digitos = [...ean].map(Number);
  const verificador = digitos.pop();
  const suma = digitos.reverse().reduce((s, d, i) => s + d * (i % 2 === 0 ? 3 : 1), 0);
  return (10 - (suma % 10)) % 10 === verificador;
}

/** Valida lo que manda el formulario. `hoy` es la fecha en Argentina (AAAA-MM-DD). */
export function validarReporte(d, hoy) {
  const errores = [];
  const producto = texto(d.producto);
  if (producto.length < 2 || producto.length > 80) errores.push("Escribí el nombre del producto (entre 2 y 80 letras).");
  const ean = texto(d.ean).replace(/\D/g, "");
  if (ean && !eanValido(ean)) errores.push("El código de barras no es válido. Revisalo o dejalo vacío.");
  const tienda = texto(d.tienda);
  if (tienda.length < 2 || tienda.length > 40) errores.push("Elegí o escribí el súper.");
  const provincia = texto(d.provincia);
  if (!PROVINCIAS.includes(provincia)) errores.push("Elegí la provincia.");
  const localidad = texto(d.localidad).slice(0, 60);
  const unidad = UNIDADES.includes(d.unidad) ? d.unidad : "unidad";
  const precio = Number(String(d.precio ?? "").replace(",", "."));
  if (!Number.isFinite(precio) || precio <= 0 || precio >= 10_000_000) errores.push("El precio tiene que ser un número mayor a 0.");
  const fecha = texto(d.fecha) || hoy;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(fecha) || fecha > hoy || diasEntre(fecha, hoy) > 7) {
    errores.push("La fecha tiene que ser de los últimos 7 días.");
  }
  let foto = null;
  if (d.foto) {
    // Una imagen JPEG en base64 empieza con "/9j/".
    if (typeof d.foto !== "string" || !d.foto.startsWith("/9j/")) errores.push("La foto tiene que ser JPEG.");
    else if (Math.floor((d.foto.length * 3) / 4) > MAX_FOTO_BYTES) errores.push("La foto es muy pesada.");
    else foto = d.foto;
  }
  return {
    ok: errores.length === 0,
    errores,
    datos: {
      producto, ean: ean || null, tienda, provincia, localidad: localidad || null, unidad,
      precio: Math.round(precio * 100) / 100, oferta: Boolean(d.oferta), fecha, foto,
    },
  };
}

export const claveProducto = (r) => r.ean || sinTildes(r.producto);

/** ¿El reporte `previo` confirma al `nuevo`? */
export function confirma(nuevo, previo) {
  const minimo = Math.min(previo.precio, nuevo.precio);
  return (
    previo.ip_hash !== nuevo.ip_hash &&
    claveProducto(previo) === claveProducto(nuevo) &&
    sinTildes(previo.tienda) === sinTildes(nuevo.tienda) &&
    previo.provincia === nuevo.provincia &&
    previo.unidad === nuevo.unidad &&
    Math.abs(diasEntre(previo.fecha, nuevo.fecha)) <= DIAS_PARA_CONFIRMAR &&
    minimo > 0 &&
    Math.abs(previo.precio - nuevo.precio) / minimo <= DIFERENCIA_PARA_CONFIRMAR
  );
}

/** CSV con comillas cuando hace falta; las filas son objetos. */
export function aCsv(filas, columnas) {
  const celda = (v) => {
    const s = v === null || v === undefined ? "" : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  return [columnas.join(","), ...filas.map((f) => columnas.map((c) => celda(f[c])).join(","))].join("\n") + "\n";
}

/** Fecha de hoy en Argentina (UTC-3 todo el año). */
export function hoyEnArgentina(ahora = Date.now()) {
  return new Date(ahora - 3 * 3600e3).toISOString().slice(0, 10);
}
