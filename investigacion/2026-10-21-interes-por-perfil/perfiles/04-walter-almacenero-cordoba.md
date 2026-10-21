# Walter, 51, dueño de un autoservicio, Córdoba (Alta Córdoba)

Compra en mayoristas y distribuidores, remarca con cada lista nueva. Tiene punto de venta con lector de código de barras. Está en un grupo de almaceneros y en una cámara de comercio barrial.

**¿Le interesa?**
Depende. Le pongo 6/10. Volvería una vez por semana, cuando me llega la lista del mayorista, para mirar "Ordenar por: Mayor aumento". Lo pasaría al grupo de WhatsApp de almaceneros y a la cámara. A los clientes no se lo mando ni loco, porque es como darles el argumento para decirme que "en el Cordiez está más barato".

**Primeros 5 segundos:**
"Una página amarilla que compara súper y dice cuánto suben. Hoy el más barato es Día" (cap. 1). La entendí como algo para el que compra, no para el que vende.

**Lo que le sirve**
- La búsqueda por código de barras anda. Puse 7790387013610 y me apareció la Taragüi 1 kg en 8 cadenas. Al abrirla: "$ 5.747 $ 3.790 Oferta −34 %" en Día. Así sé exactamente contra qué me comparan.
- Muestra el precio sin oferta (el CSV trae `precio_lista`). Yo me tengo que medir contra la lista, no contra la oferta de un día.
- "Mayor aumento" me sirve para decidir qué remarcar.
- Como cliente, me sirve el dato de "hasta 55 % más según dónde lo compres".

**Lo que no entiende o lo frena**
- Se contradice. Arriba dice "Hoy el más barato es Día" (cap. 1) y abajo "Cordiez (Córdoba) sale 11,7 % menos que el súper típico", con Día en −7,5 %. ¿Al final cuál es el más barato?
- "Súper típico": en ningún lado dice qué es.
- La cinta "FIDEOS SPAGHETTI MATARAZZO 500 G $ 1.889 EN TOLEDO" (cap. 2-3). Toledo es de Mar del Plata, a mí qué me importa.
- Dice "sin elegir sucursal ni código postal". ¿El Carrefour de la web cobra lo mismo que el de Córdoba?
- El índice marca "+0,3 %" "Desde el 20 de octubre de 2026" (cap. 11): son dos días, todavía no me dice nada. Y "Lácteos −0,0 %" (cap. 12): ¿bajó o no bajó?
- En las cap. 8 a 11 los títulos casi no se leen (rojo sobre rojo, gris sobre negro). Puede ser la animación de entrada, pero si scrolleás rápido no los ves.
- La carga de precios todavía no anda: "La carga de precios abre en los próximos días" (cap. 8). Además dice "nos ayudás a medir lo que las webs no muestran: … almacenes de barrio", y eso me pone nervioso. ¿Van a comparar mi precio de lista con la oferta del Cordiez?
- Para buscar hay que tipear los 13 números del código. No hay forma de escanearlo con la cámara.

**Lo que le falta para usarlo seguido**
- Un filtro por Córdoba.
- Una columna con precios mayoristas.
- Poder comparar mi propia lista.
- Segundas marcas y más productos (49 son poquitos).
- Un aviso semanal por WhatsApp.

**¿Cómo podría aportar al proyecto?**
Del sistema saco un CSV con código y precio de los 49 productos. Para mandarlo necesitaría:
- Carga masiva. Hoy es de a uno, con captcha y con un tope de 30 por día.
- Figurar solo como "Almacén o autoservicio de barrio", sin nombre ni dirección.

Los precios mayoristas los pasaría a través de la cámara, juntando los de varios almacenes. La lista de Yaguar con mi cuenta no la paso.

Los riesgos que veo:
- Que un competidor o un cliente cargue mal mi precio.
- Que salga un titular tipo "los almacenes, 20 % más caros" sin aclarar que el Cordiez compra por camión y yo por bulto, con flete.

**Frase textual**
"Muchachos, miren esto: ponés el código de barras y te dice cuánto sale en cada súper. Ojo que el Cordiez da 11 % abajo del promedio, por eso nos lo tiran en la cara. Sirve para ver qué remarcar, pero no sé si son precios de acá y tiene dos días de datos."

**Top 3 cambios**
1. Poder elegir ciudad o provincia: que muestre solo las cadenas que hay en Córdoba y que el titular diga cuál es el más barato acá.
2. Un "Compará tu lista": subo el CSV del sistema y me dice, en privado y sin publicar nada, cuánto estoy arriba o abajo de cada cadena (con precio de lista) y del mayorista.
3. Ampliar la canasta con segundas marcas, sumar carga masiva para comerciantes y un resumen semanal por WhatsApp con lo que más subió.

---
Notas de la prueba (fuera del personaje):
- Probé el buscador en el sitio local. Por código de barras y por "yerba" funciona. "Cordiez" y "Cofler" dan 0 resultados: no se puede filtrar por cadena.
- Cordiez tiene 42 de los 49 productos (por ejemplo, no tiene la Taragüi 1 kg).
- El formulario de carga no está activo. Entre los lugares para elegir figura "Almacén o autoservicio de barrio"; el campo "Nombre del lugar" aparece solo con "Otro lugar".
