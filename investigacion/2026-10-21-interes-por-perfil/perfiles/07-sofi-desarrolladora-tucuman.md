# Sofi, 29, desarrolladora backend, de Tucumán

Python y TypeScript en una fintech. Contribuye a proyectos de datos abiertos y hace scrapers por hobby. Tiene unas horas el finde y una comunidad de devs del NOA en Discord.

**¿Le interesa?**
Depende. Le pongo un 7/10. Estrella sí, ya. Contribuiría un finde si el autor abre issues. Lo comparto en el Discord del NOA ahora; en LinkedIn lo comparto cuando haya una cadena del norte.

**Primeros 15 minutos con el repo:**
- Lo instalé con venv, pip y `[dev]` en Python 3.13 (pandas 3, duckdb 2). Corrieron **45 tests en 0,8 s**, y también pasan con los sockets bloqueados, así que funcionan sin internet de verdad. Los 8 tests en Node del worker también pasan. `changuito calcular` y `sitio` andan si les pasás `--datos` y `--salida`.
- Lo que faltó:
  - No hay CONTRIBUTING, ni plantillas de issue o PR, ni labels. Hay **0 issues** en GitHub.
  - No hay linter configurado.
  - Son 12 commits en 3 días de un solo autor: si él se va, el proyecto se cae.
  - El README está desactualizado: el diagrama dice "API de 6 súper" (README.md:29) y la estructura no menciona `fuentes/coto.py` ni `comunidad/`.
  - El README no menciona `--datos`. Si seguís los pasos, `changuito recolectar` escribe en `data/` del repo y te choca con el commit diario del bot.
  - La carga comunitaria no está activa: `comunidad/sitio.json` tiene la `url` vacía.

**Lo que está bien hecho:**
- Son ~800 líneas de Python legible, con docstrings que explican el porqué (VTEX da 400 con "+"; el ListPrice de Cencosud viene ×100).
- La metodología está documentada (Jevons, precio de lista contra promo) y las limitaciones son honestas, incluido "sin elegir sucursal ni código postal".
- Usa git scraping, tiene licencia MIT y deja descargar el CSV diario.
- El worker valida el dígito verificador del EAN, guarda la IP hasheada, confirma con otra persona y pide la provincia.

**Barreras para contribuir:**
1. **Sumar una cadena que no sea VTEX:** `recolectar.py:40` tiene cableado `if tienda == coto.TIENDA`. No hay una interfaz de fuente, así que una tercera fuente es otro `if`.
2. **Sumar una cadena VTEX:** toca varios lugares y no está documentado. Están `vtex.py:18` (TIENDAS), `sitio.py:17` (NOMBRES_TIENDAS) y `sitio.py:29` (REGIONES). También hay textos fijos en `plantilla.html:542`, `vtex.py:3` y el README.
3. **Región:** `_buscar` (`vtex.py:92-95`) consulta sin sales channel ni región, así que "Vea" es el precio por defecto, que seguramente es el de AMBA. Hay un solo índice nacional, sin corte por región.
4. **Tests:** usan JSON sintético y no hay respuestas reales grabadas. Si una API cambia, te enterás recién cuando falla el cron.
5. **`changuito buscar`:** sin red tira un traceback crudo (`__main__.py:66`) y solo acepta tiendas VTEX (`:93`).

**Primeras contribuciones que haría:**
1. `CONTRIBUTING.md` y plantillas en `.github/ISSUE_TEMPLATE/` para "sumar cadena" y "sumar producto", con un "no commitees `docs/` ni `data/`".
2. Un registro único de cadenas, con nombre, región, plataforma y `sc`. Toca `vtex.py`, `sitio.py` y `plantilla.html:542`.
3. Un protocolo `Fuente` con registro en `recolectar.py:39-42`.
4. Fixtures grabadas por cadena en `tests/fixtures/`, con un test por tienda.
5. Manejo de errores y soporte de Coto en `buscar`, ruff en `tests.yml` y arreglos del README. También unificar "ChangoMás" y "Más Online" en `sitio.py:53`: es la misma cadena.

**¿Cómo podría aportar más allá del código?**
- Relevar qué súper del NOA venden online y con qué plataforma (Libertad, Vea NOA). No pude verificarlo desde acá porque el proxy bloqueó las consultas.
- Investigar los sales channels de VTEX que corresponden al NOA.
- Armar una hackatón de un finde para sumar SEPA / Precios Claros, que ya está en las "Ideas para seguir" del README. Tiene sucursales de todo el país, y eso sí rompe el sesgo AMBA.
- Hacer una campaña de carga de precios de góndola en Tucumán, Salta y Jujuy cuando se active el formulario.
- Lo que necesito del autor:
  - Que abra 5 a 10 issues etiquetadas.
  - Que diga si acepta un índice por región.
  - Que despliegue el worker.
  - Que revise los PR rápido y abra Discussions.

**Frase textual para el Discord:**
"Che, miren esto: índice de inflación de súper que corre solo con GitHub Actions + DuckDB, 45 tests que pasan sin internet en un segundo, código cortito y prolijo. El drama: de 9 cadenas, 7 son las de siempre de AMBA y las otras son de Córdoba y Mardel. Del NOA, nada. Sumar una cadena VTEX es casi una línea… ¿alguien se fija si Libertad o Vea Tucumán exponen la API? Si el autor abre issues, armamos un finde 🧉"

**Top 3 cambios para atraer contribuidores:**
1. Abrir issues "good first issue" y escribir un CONTRIBUTING con "sumar una cadena en 5 pasos".
2. Armar el registro único de cadenas con región y la interfaz de fuentes, para que sumar una cadena del NOA sea un PR de un archivo más una fixture.
3. Comprometerse con lo regional: índice y ranking por región (vía `sc` de VTEX o SEPA) y activar la carga comunitaria por provincia.
