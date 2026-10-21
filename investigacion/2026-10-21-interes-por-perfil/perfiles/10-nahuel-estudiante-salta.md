# Nahuel, 22, estudiante de Agronomía, Salta

De Orán, vive con la beca Progresar y hace delivery. Compra en Vea, Carrefour, el Mercado San Miguel y súper locales. Milita en el centro de estudiantes, que releva el costo de vida estudiantil cada cuatrimestre.

**¿Le interesa?**
Depende. Le pongo 4/10 hoy. Volvería solo si aparece Salta. Lo pasaría al grupo de WhatsApp de la comisión del centro, pero como base para salir a relevar, no como dato. A Instagram no lo subo: me dirían "eso es Buenos Aires".

**Primeros 5 segundos.**
"Cuánto sube el súper" se entiende al toque. Después leo "Cordiez (Córdoba) y Toledo (Mar del Plata). Hoy el más barato es Día." (captura 01) y pienso: Córdoba y Mar del Plata sí, el NOA no. Y un Día cerca no tengo. (Encima acá "changuito" es un pibe chico.)

**Lo que le sirve.**
- El buscador. La "Yerba Playadito 1 kg" va de $ 5.099 a $ 5.289 y te muestra el código de barras. Para la planilla de la casa me sirve para ver si una oferta de Vea es oferta de verdad.
- Los 49 productos con su código de barras. Podemos usar esa misma lista en nuestro relevamiento y comparar Salta contra la web.
- "Descargar los precios de hoy" (el CSV) y el "Cómo citar", para poner en la nota al Consejo Superior.

**Lo que no entiende o lo frena.**
- Arriba no dice nunca "AMBA". Lo único está abajo de todo: "Usa precios online sin elegir sucursal, que pueden variar en tu zona". Con eso no sé si el Vea de acá cobra lo mismo que la web.
- "+0,3 %" "Desde el 20 de octubre de 2026" (captura 11): son dos días de datos. Para este cuatrimestre todavía no me sirve.
- "no incluye carnes, frutas, verduras ni huevos", que es justo lo que compramos en el San Miguel.
- "La carga de precios abre en los próximos días." (captura 08). La única parte pensada para nosotros todavía no anda.
- Al bajar, el texto se ve lavado, casi no se lee (capturas 03, 08 y 09), y aparece un bloque rojo vacío (captura 10).

**Lo que le falta para usarlo seguido.**
Un filtro por provincia. Cuánto sale la canasta entera en pesos en cada súper, porque "por cada $ 1.000… $ 75 menos" no me sirve para comparar con el Progresar. Y la serie histórica para bajar sin tener que meterse en GitHub.

**¿Cómo podría aportar al proyecto?**
El centro podría hacer una jornada de carga por mes en Vea, Carrefour, Libertad y el San Miguel (en el código está la opción "Feria o mercado"). Pero leí comunidad/README.md y el código, y hay problemas:
- El tope es de 30 precios por día por IP.
- Dos cargas que salen de la misma IP no se confirman entre sí.
- Si cargamos todos desde el wifi de la facu, el sistema nos cuenta como una sola persona.
- Si elegís "Otro lugar", hay que escribir el nombre igual que el otro para que confirme: "San Miguel" no es lo mismo que "Mercado San Miguel".
- La localidad no cuenta, así que un precio de Orán confirma uno de Salta capital.
- Lo que se carga "Por ahora no entra al índice".

Para que nos sirva haría falta un modo grupal (cargar desde planilla), resolver lo del wifi compartido y poder bajar lo cargado de Salta.

**Frase textual.**
"Compañeros, la página está buena pero mide Buenos Aires. Si queremos que el rectorado nos crea, los precios de Salta los tenemos que poner nosotros: misma lista, mismos códigos de barras, y la comparamos con la web."

**Top 3 cambios.**
1. Precios por provincia, y un aviso bien visible arriba de que hoy son mayormente precios de AMBA.
2. Abrir la carga con modo grupal: desde planilla, sin que el wifi compartido nos frene, y con descarga de lo cargado por provincia.
3. Costo total de la canasta en pesos en cada súper, con historial, para compararlo con la beca.
