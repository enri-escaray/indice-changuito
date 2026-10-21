# ¿A quién le interesa el Índice Changuito y quién puede sumar?

Prueba con 10 usuarios simulados, el 21/10/2026. Cada agente hizo de una persona distinta: familias, un
jubilado y sectores que podrían aportar al proyecto. Miró el sitio en capturas de celular o compu, leyó
el HTML y el código, y probó el buscador en un navegador. Las preguntas fueron dos: **¿le interesa?** y
**¿cómo podría aportar?**

Son simulaciones: sirven para encontrar fricciones y armar hipótesis, no reemplazan hablar con gente
real. Los informes completos de cada perfil están en [`perfiles/`](perfiles/).

## En una tabla

| Perfil | Nota | ¿Vuelve? | ¿Lo comparte? | ¿Puede aportar? | Qué aportaría |
|---|:-:|---|---|:-:|---|
| [Romina](perfiles/01-romina-madre-la-matanza.md), madre, La Matanza | 5 | Una vez por mes | Captura al grupo de mamás y de ofertas | Bajo | Precios del chino y la verdulería; difusión en grupos |
| [Martín](perfiles/02-martin-padre-rosario.md), padre, Rosario | 6 | Cada 2 o 3 semanas | Grupo del fútbol, para discutir | Bajo | Foto del ticket de súper de Rosario, si le lleva menos de un minuto |
| [Héctor](perfiles/03-hector-jubilado-mar-del-plata.md), jubilado, Mar del Plata | 6 | Todas las semanas | Centro de jubilados, de viva voz | **Alto** | Su libretita (historial), controlar web contra góndola, tickets de los socios |
| [Walter](perfiles/04-walter-almacenero-cordoba.md), almacenero, Córdoba | 6 | Todas las semanas | Grupo de almaceneros y cámara; a clientes, no | Medio | CSV de su sistema con código de barras; precios mayoristas a través de la cámara |
| [Graciela](perfiles/05-graciela-comedor-varela.md), comedor, Florencio Varela | 5 | Todas las semanas | Voluntarias; a la mesa de organizaciones, con meses de datos | **Alto** | Más de un año de compras en planilla; voluntarias; red de comedores |
| [Dra. Ferreyra](perfiles/06-ferreyra-economista.md), economista | 6 / 3 | — | En redes: "prometedor, pero ojo" | **Alto** | Revisión de método, tesistas, ponderadores |
| [Sofi](perfiles/07-sofi-desarrolladora-tucuman.md), desarrolladora, Tucumán | 7 | — | Discord del NOA ya; LinkedIn cuando haya una cadena del norte | **Alto** | Código, cadenas del NOA, hackatón para sumar SEPA |
| [Dr. Paz](perfiles/08-paz-defensa-consumidor.md), defensa del consumidor | 6 | — | Lo recomendaría para comparar, no como prueba | **Alto**, con condiciones | 15 a 20 voluntarios en CABA, Mendoza y Neuquén; góndola contra caja |
| [Cami](perfiles/09-cami-creadora-contenido.md), creadora de contenido | 6 | Un video por semana | Sí, a 180 mil seguidores | Medio | Difusión y campaña de carga de precios |
| [Nahuel](perfiles/10-nahuel-estudiante-salta.md), estudiante, Salta | 4 | Solo si aparece Salta | Comisión del centro de estudiantes | Medio | Jornadas de carga en Salta; su relevamiento de costo de vida |

**Promedio: 5,7 de 10.** Nadie dijo que no, pero nadie pasó de 7: los diez respondieron "depende". La
economista separó la nota: 6 como fuente de datos abiertos y 3 como índice de inflación, por ahora.

## Lo que se repite

Ordenado por cuántos perfiles lo dijeron.

1. **"Lo más barato está en Córdoba" (8 de 10).** En el buscador, el "más barato en" cae seguido en
   Cordiez o Toledo, que la mayoría no tiene cerca. Martín contó: de los 49 productos, 21 salen más
   baratos en Cordiez y 5 en Toledo. Lo que piden es **elegir zona o "mis súper"** y que todo se
   recalcule con eso. Es el pedido número uno.
2. **El índice todavía no dice nada (8 de 10).** "+0,3 % desde el 20 de octubre" son dos días, y
   "Lácteos −0,0 %" parece un error. Además, la economista mostró que cerca de ¾ de ese +0,3 % sale de
   Cencosud: el Nesquik pasó de $ 5.100 a $ 6.654 en Disco y Jumbo cuando terminó una promo
   (verificado en `data/precios/2026/10/`).
3. **Quieren cargar precios, pero como está no les sirve (7 de 10).** Ver
   [más abajo](#la-carga-de-precios-la-quieren-los-que-más-pueden-aportar).
4. **La canasta no es la del bolsillo flaco (6 de 10).** Faltan pañales, segundas marcas (Marolio,
   marca Día), lentejas, leche en polvo, carne, huevos, verdura y, para el asado, fernet y cerveza.
5. **"Armá tu lista" con el total en pesos (6 de 10).** Tildar lo que llevan y ver cuánto sale en cada
   súper. "Por cada $ 1.000 gastás $ 75 menos" se entiende, pero no sirve para comparar con una beca o
   una jubilación.
6. **El titular choca con el gráfico (6 de 10).** Arriba dice "Hoy el más barato es Día" y el gráfico
   pone primero a Cordiez (−11,7 % contra −7,5 %). Nadie sabe qué es el "súper típico".
7. **"Sin 2x1 ni descuentos con tarjeta" deja afuera lo que usan (5 de 10).** Mercado Pago, promos de
   bancos y el descuento a jubilados de los miércoles.
8. **Falta algo listo para compartir (5 de 10).** Una imagen vertical para estados e historias, un
   informe de una página para imprimir, y que la vista previa del link muestre el dato del día. Hoy
   muestra la foto del changuito, que pesa 1,1 MB.
9. **Bloques vacíos al bajar (4 de 10).** Las animaciones de entrada dejan secciones vacías o lavadas
   si se baja rápido, se graba la pantalla o el celular es lento. En parte salió de cómo se sacaron
   las capturas (con 1,5 s de espera se ven bien), pero en una grabación de pantalla pasa de verdad.

## La carga de precios: la quieren los que más pueden aportar

Jubilados, comedores, estudiantes y la asociación de consumidores quieren cargar precios de góndola.
Es justo lo que el sitio no puede medir solo. Hoy los frena esto, y está confirmado en
`comunidad/src/`:

- **Todavía no está abierta:** "La carga de precios abre en los próximos días", y
  `comunidad/sitio.json` no tiene `url`.
- **Wifi compartido:** el tope es de 30 precios por día *por IP*, y dos cargas de la misma IP no se
  confirman entre sí. Un centro de estudiantes o un comedor cargando desde el mismo wifi cuenta como
  una sola persona.
- **"Se publica cuando otra persona carga el mismo":** en La Perla o en Echesortu, ¿quién más va a
  cargar ese mismo precio? Si no ven publicado lo que cargaron, dejan de cargar ("laburé al pedo").
- **De a uno, con captcha cada vez:** piden subir un ticket entero o una planilla.
- **Sin fecha en el formulario**, aunque el servidor acepta hasta 7 días atrás. Héctor quiere pasar lo
  de su libretita.
- **Faltan opciones:** mayorista, "chino" y "por bulto".
- **No se usa la localidad:** un precio de Orán confirma uno de Salta capital.
- **Lo que se carga "por ahora no entra al índice".**
- **Falta lo legal:** términos de uso, política de privacidad (Ley 25.326), cuánto tiempo se guardan las
  fotos, aviso de tapar la tarjeta en la foto del ticket y un mail de contacto que no sea GitHub.

## Sectores que pueden aportar, en orden

| # | Sector | Qué trae | Qué necesita del proyecto |
|:-:|---|---|---|
| 1 | **Universidad** (economía, estadística) | Credibilidad, revisión de método, tesistas para validar contra SEPA y el IPC | Arreglar Cencosud y los huecos; panel histórico descargable; registro de cambios; aceptar revisiones |
| 2 | **Desarrolladores de datos abiertos** | Código, cadenas regionales, SEPA para cubrir todo el país | CONTRIBUTING, 5 a 10 issues etiquetadas, un registro único de cadenas, decir si se acepta un índice por región |
| 3 | **Jubilados y centros de jubilados** | Tiempo, prolijidad, libretas con historial, control de web contra góndola | Fecha en el formulario, ticket entero de una vez, ver qué pasó con lo cargado; comparar con la mínima |
| 4 | **Comedores y organizaciones sociales** | Más de un año de compras, voluntarias, red en el conurbano | Mayoristas, "por bulto", informe para imprimir, que no figure el nombre del comedor |
| 5 | **Asociaciones de consumidores** | Voluntarios en provincias, aval, góndola contra caja | Términos y privacidad, mail de contacto, carga en lote, tres meses de serie antes de avalar |
| 6 | **Centros de estudiantes del interior** | Cobertura fuera de AMBA | Modo grupal, solución al wifi compartido, descarga por provincia |
| 7 | **Creadores de contenido** | Difusión | Imágenes listas para compartir y un contador de precios cargados. Cami fue clara: si el proyecto acepta plata de un súper, deja de citarlo |
| 8 | **Almaceneros y cámaras** | Precios de barrio y mayoristas | Carga masiva anónima y una comparación privada de su lista. Tienen miedo de quedar escrachados |
| 9 | **Familias** | Uso y difusión en grupos de WhatsApp | Aportan solo si cargar lleva menos de un minuto y ven publicado lo que cargaron |

## Errores encontrados en el código

Verificados en el código, no solo en la opinión de los agentes:

- **El índice se mueve con promos de Cencosud.** `fuentes/vtex.py`, `precio_de_lista`: en Jumbo, Disco
  y Vea el precio de lista es el de venta, así que el fin de una promo cuenta como aumento.
- **Un precio que falta más de 7 días pierde su variación.** `indice.py`: `ffill(limit=7)` y después
  `diff()` dan NaN cuando el precio vuelve, y esa suba no entra nunca al índice.
- **Dentro de cada categoría todos los productos pesan igual**, en `indice_por_categoria`.
- **La primera inflación mensual comparará noviembre contra un octubre de 12 días.**
- **El texto de "Compartir" dice "6 supermercados" y son 9**, en `plantilla.html:1250`.
- **El README dice "API de 6 súper"** (línea 29) y no menciona `fuentes/coto.py` ni `comunidad/`.
- **Buscar por cadena** ("toledo", "cordiez") no devuelve nada.
- **"Más Online" es la web de ChangoMás, pero nadie la reconoce por ese nombre**, y en la lista de la
  carga (`sitio.py:53`) ChangoMás aparece aparte.
- **El detalle de cada producto va en gris a 13 o 14 px** (`--paso-chico`), chico para gente grande.

## Próximos pasos propuestos

**Rápidos (horas):**
- corregir "6 supermercados" y el README;
- titular "el más barato entre las cadenas nacionales" y explicar qué es el "súper típico";
- presentar el índice como "en construcción" hasta tener 30 días;
- hacer instantáneas las animaciones de entrada;
- poder buscar por cadena.

**Medianos (días):**
- selector de zona o "mis súper";
- sacar a Cencosud del índice hasta tener su precio de referencia, y arreglar los huecos largos;
- "Armá tu lista" con el total en pesos;
- CONTRIBUTING con issues para principiantes.

**Para abrir la carga:**
- campo de fecha y ticket entero;
- mostrar como "sin confirmar" lo que nadie confirmó, en vez de esconderlo;
- un modo para organizaciones que no dependa de la IP;
- opciones mayorista, chino y por bulto;
- términos, privacidad y mail de contacto.

**Grandes:**
- sumar SEPA para tener sucursales de todo el país;
- ampliar la canasta con segundas marcas y frescos (vía la comunidad);
- comparar con la jubilación mínima y con el IPC.
