// Página de moderación: lista los precios pendientes con su foto y permite aprobarlos o rechazarlos.
// La clave de admin se guarda solo en la pestaña (sessionStorage) y viaja en el encabezado Authorization.
export const PAGINA_ADMIN = `<!doctype html>
<html lang="es-AR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Moderación · Índice Changuito</title>
<style>
  body { margin: 0; font: 16px/1.5 system-ui, sans-serif; background: #FFE11A; color: #000; }
  main { max-width: 960px; margin: 0 auto; padding: 24px 16px 64px; }
  h1 { font-size: 32px; margin: 0 0 16px; }
  form, .fila { background: #fff; border-radius: 20px; padding: 16px 20px; margin-bottom: 12px; }
  input { font: inherit; padding: 10px 14px; border: 2px solid #000; border-radius: 999px; width: min(100%, 360px); }
  button { font: inherit; font-weight: 600; padding: 10px 20px; border: 0; border-radius: 999px; background: #000; color: #FFE11A; cursor: pointer; }
  button.rechazar { background: #C8102E; color: #fff; }
  .fila { display: grid; grid-template-columns: 1fr auto; gap: 12px; align-items: center; }
  .fila img { max-width: 220px; border-radius: 12px; display: block; margin-top: 8px; }
  .acciones { display: flex; gap: 8px; flex-wrap: wrap; }
  .vacio { background: #fff; border-radius: 20px; padding: 20px; }
</style></head><body><main>
<h1>Precios pendientes</h1>
<form id="acceso"><label>Clave de admin <input type="password" id="clave" autocomplete="current-password"></label> <button>Entrar</button></form>
<div id="lista"></div>
<script>
const pedir = (ruta, opciones = {}) => fetch(ruta, { ...opciones, headers: { ...(opciones.headers || {}), Authorization: "Bearer " + sessionStorage.getItem("clave") } });
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
async function cargar() {
  const r = await pedir("/admin/pendientes");
  const lista = document.getElementById("lista");
  if (r.status === 401) { lista.innerHTML = '<p class="vacio">Clave incorrecta.</p>'; return; }
  const { pendientes } = await r.json();
  document.getElementById("acceso").hidden = true;
  if (!pendientes.length) { lista.innerHTML = '<p class="vacio">No hay precios pendientes.</p>'; return; }
  lista.innerHTML = pendientes.map((p) => '<div class="fila" id="r' + p.id + '"><div><strong>' + esc(p.producto) + '</strong> ' + (p.ean ? '(' + esc(p.ean) + ')' : '') +
    '<br>$ ' + esc(p.precio) + ' por ' + esc(p.unidad) + (p.oferta ? ', en oferta' : '') + ' en ' + esc(p.tienda) + ', ' + esc(p.localidad || '') + ' ' + esc(p.provincia) +
    '<br><small>Precio del ' + esc(p.fecha) + ', cargado ' + esc(p.creado) + '</small>' +
    (p.tiene_foto ? '<img alt="Foto que mandó la persona" data-id="' + p.id + '">' : '') + '</div>' +
    '<div class="acciones"><button data-moderar="aprobado" data-id="' + p.id + '">Aprobar</button><button class="rechazar" data-moderar="rechazado" data-id="' + p.id + '">Rechazar</button></div></div>').join("");
  for (const img of lista.querySelectorAll("img[data-id]")) {
    const f = await pedir("/admin/foto?id=" + img.dataset.id);
    if (f.ok) img.src = URL.createObjectURL(await f.blob());
  }
}
document.getElementById("acceso").addEventListener("submit", (e) => { e.preventDefault(); sessionStorage.setItem("clave", document.getElementById("clave").value); cargar(); });
document.getElementById("lista").addEventListener("click", async (e) => {
  const b = e.target.closest("[data-moderar]"); if (!b) return;
  const r = await pedir("/admin/moderar", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: b.dataset.id, estado: b.dataset.moderar }) });
  if (r.ok) document.getElementById("r" + b.dataset.id).remove();
});
if (sessionStorage.getItem("clave")) cargar();
</script></main></body></html>`;
