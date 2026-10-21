# Dra. Lucía Ferreyra, 41, economista (CONICET y UNLP)

Docente de Estadística Económica, asesora a una consultora de precios. Conoce el IPC del INDEC, PriceStats y SEPA. Dirige tesistas. Unos 15 mil seguidores en redes.

**¿Le interesa?**
Depende. Le pongo 6/10 como fuente de microdatos abiertos y 3/10 como "índice de inflación", por ahora. Como medida de inflación no lo citaría todavía. Como fuente de precios online sí, citando repo y commit. Lo compartiría en redes con un tono de "prometedor, pero ojo: el primer +0,3 % es casi todo artefacto". Con tesistas sí lo usaría, como insumo y como ejercicio de replicación y detección de sesgos.

**Primeros 5 segundos.**
"Cuánto sube el súper" y el changuito: se entiende al toque. Pero el héroe dice "el más barato es Día" y el gráfico del ranking pone primero a Cordiez (−11,7 % contra −7,5 %). Más abajo aparece un "+0,3 %" gigante armado con dos observaciones (capturas 01 y 09).

**Fortalezas metodológicas.**
- El matching por EAN compara exactamente el mismo producto, así que no hay problema de sustitución.
- Usa Jevons en el nivel elemental y un agregado de pesos fijos tipo Laspeyres.
- Separa bien el precio de lista (para el índice) del precio que se paga (para el ranking).
- Con el git scraping, los microdatos quedan versionados y reproducibles, y tiene tests.
- Declara sus limitaciones con honestidad.
- Los precios que carga la gente no entran al índice.

**Problemas metodológicos o de comunicación**
*Verificados en el código y recalculando con `indice.calcular`:*
1. **El titular es un artefacto de Cencosud.** En Jumbo, Disco y Vea el precio de lista se reemplaza por el precio de venta (`vtex.py` L43-52). El Nesquik pasó de 5.100 a 6.654 en Disco y Jumbo (+30,5 %). La harina Favorita en Vea pasó de 990 a 1.290, cuando el resto estaba a ~1.300. Sacando esos dos casos el general da +0,075 %; sin Cencosud, +0,057 %. O sea, cerca de ¾ del +0,3 % es eso. El "Azúcar y dulces +2,6 %" es casi todo Nesquik.
2. **Un hueco de más de 7 días borra la variación.** El `ffill(limit=7)` (`indice.py` L71) seguido de `diff()` (L79) deja NaN cuando el precio reaparece. Lo probé con un caso sintético: 100 → 150 después de 9 días sin precio y el índice queda en 100. Es un sesgo a la baja, justo en el caso típico de faltante antes de un aumento.
3. **Dentro de cada categoría todos los productos pesan igual** (L92). Unas Oreo pesan lo mismo que la harina, y las categorías no son agregados elementales.
4. **El titular del ranking excluye a las regionales a propósito** (`plantilla.html` L632). Además, la ventaja de Día es por promos: con precio de lista queda en −0,2 %. En tres días osciló entre −10,4, −2,7 y −7,5.
5. **La primera inflación mensual compara noviembre contra un "octubre" de 12 días** (del 20 al 31). Si los precios vienen subiendo, eso la subestima.
6. **"Sin contar ofertas… hasta 55 %" no se cumple en Cencosud:** ahí el precio de lista ya es el de oferta.
7. **Documentación:** la cita no tiene autor ni versión, y el diagrama del README dice "API de 6 súper" cuando son 9.

*Sospechas, sin verificar:*
- El ListPrice de Día podría ser un precio tachado inflado: la Milka subió de lista de 5.140 a 5.440 el mismo día que entró en promo.
- Los precios online sin sucursal mezclan geografías en el "súper típico".

**Lo que le falta para tomarlo en serio**
- El panel histórico en un solo CSV o JSON, más una API. Hoy solo se descarga `precios-hoy.csv`.
- Diccionario de datos.
- DOI (un release en Zenodo).
- Changelog de la canasta y de las cadenas.
- Ponderadores ENGHo/IPC del INDEC por región, con pesos dentro de cada categoría.
- Imputación por media de clase y una bandera de outliers (por ejemplo, variaciones diarias de más del 20 %).
- Comparación con el IPC de GBA y con SEPA.

**¿Cómo podría aportar al proyecto?**
- Abriría un issue con una nota metodológica y los puntos 1 a 5.
- Le ofrecería al autor un tesista de la UNLP para validar la serie contra SEPA y el IPC, o una tesina con un convenio liviano.
- Me ofrecería para revisar los ponderadores.

Del autor necesito tres cosas: el panel histórico en formato largo, un registro de cambios y que acepte una revisión metodológica antes de cada cambio de método.

**Frase textual**
"Interesante el Índice Changuito: EAN por EAN, Jevons, datos abiertos en GitHub. Pero ojo: con 2 días de serie, ~¾ del +0,3 % sale de dos promos de Cencosud que terminaron (Nesquik y harina). Como microdato, sí; como inflación, todavía no. Ojalá le sume ponderadores INDEC y un DOI."

**Top 3 cambios**
1. Resolver Cencosud: conseguir su precio de referencia o sacarlo del índice, filtrar outliers y no titular un número mientras haya menos de 30 días de serie.
2. Corregir la imputación de huecos largos y ponderar dentro de las categorías con la ENGHo.
3. Publicar el panel histórico con diccionario, DOI, changelog y una cita con autor y versión.
