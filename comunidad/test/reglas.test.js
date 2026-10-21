import assert from "node:assert/strict";
import { test } from "node:test";

import { aCsv, confirma, eanValido, hoyEnArgentina, validarReporte } from "../src/reglas.js";

const HOY = "2026-10-21";
const base = { producto: "Yerba Playadito 1 kg", tienda: "Coto", provincia: "Buenos Aires", precio: "5190", unidad: "unidad" };

test("códigos de barras", () => {
  assert.equal(eanValido("7793704000928"), true);
  assert.equal(eanValido("7793704000929"), false);
  assert.equal(eanValido("77956262"), true); // EAN-8 real (sal Celusal)
  assert.equal(eanValido("123"), false);
});

test("un reporte válido se normaliza", () => {
  const { ok, datos } = validarReporte({ ...base, precio: "5.190,50".replace(".", ""), ean: "7793704000928", localidad: "  Lanús  " }, HOY);
  assert.equal(ok, true);
  assert.equal(datos.precio, 5190.5);
  assert.equal(datos.localidad, "Lanús");
  assert.equal(datos.fecha, HOY);
  assert.equal(datos.ean, "7793704000928");
});

test("errores claros", () => {
  const { ok, errores } = validarReporte({ producto: "", tienda: "C", provincia: "Narnia", precio: "-3", ean: "1234", fecha: "2026-10-25" }, HOY);
  assert.equal(ok, false);
  assert.equal(errores.length, 6);
  assert.ok(errores.some((e) => e.includes("código de barras")));
  assert.ok(errores.some((e) => e.includes("últimos 7 días")));
});

test("la foto tiene que ser un JPEG chico", () => {
  assert.equal(validarReporte({ ...base, foto: "iVBORw0KGgo" }, HOY).ok, false);
  assert.equal(validarReporte({ ...base, foto: "/9j/" + "A".repeat(500_000) }, HOY).ok, false);
  assert.equal(validarReporte({ ...base, foto: "/9j/4AAQ" }, HOY).ok, true);
});

const reporte = (cambios = {}) => ({ ...validarReporte(base, HOY).datos, ip_hash: "a", ...cambios });

test("dos personas que ven el mismo precio se confirman", () => {
  assert.equal(confirma(reporte(), reporte({ ip_hash: "b", precio: 5250, fecha: "2026-10-19", tienda: "coto" })), true);
});

test("no se confirma con uno mismo ni con datos distintos", () => {
  assert.equal(confirma(reporte(), reporte()), false, "misma persona");
  assert.equal(confirma(reporte(), reporte({ ip_hash: "b", precio: 6000 })), false, "precio muy distinto");
  assert.equal(confirma(reporte(), reporte({ ip_hash: "b", provincia: "Córdoba" })), false, "otra provincia");
  assert.equal(confirma(reporte(), reporte({ ip_hash: "b", fecha: "2026-10-10" })), false, "muy viejo");
  assert.equal(confirma(reporte(), reporte({ ip_hash: "b", unidad: "kg" })), false, "otra unidad");
});

test("sin código de barras se compara por nombre, sin tildes", () => {
  const carne = { ean: null, producto: "Asado de tira", unidad: "kg" };
  assert.equal(confirma(reporte({ ...carne }), reporte({ ...carne, producto: "ASADO DE TIRA", ip_hash: "b" })), true);
  assert.equal(confirma(reporte({ ...carne, producto: "Pechuga" }), reporte({ ...carne, producto: "Pechúga", ip_hash: "b" })), true);
  assert.equal(confirma(reporte({ ...carne }), reporte({ ...carne, producto: "Vacío", ip_hash: "b" })), false);
});

test("CSV y fecha argentina", () => {
  assert.equal(aCsv([{ a: 'dice "hola", chau', b: 2 }], ["a", "b"]), 'a,b\n"dice ""hola"", chau",2\n');
  assert.equal(hoyEnArgentina(Date.parse("2026-10-22T02:00:00Z")), "2026-10-21");
});
