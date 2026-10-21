# Comunidad: carga de precios sin cuenta

Servidor chico en **Cloudflare Workers** (gratis) que recibe los precios que carga la gente desde el sitio.

- **Sin cuenta:** el formulario usa el captcha de Cloudflare (**Turnstile**) en vez de pedir login.
- **Confirmación:** un precio se publica cuando **otra persona** carga el mismo (mismo producto, súper, provincia y unidad, con hasta 3 días y 5 % de diferencia), o cuando lo **aprobás vos** en `/admin`, por ejemplo mirando la foto del ticket.
- **Privacidad:** no se guarda la IP, solo un hash con sal que sirve para no contar dos veces a la misma persona. Máximo 30 precios por persona por día.
- **Robot diario:** guarda lo confirmado en `data/comunidad/precios.csv`. Por ahora no entra al índice.

| Ruta | Para qué |
|---|---|
| `POST /precios` | Cargar un precio (lo usa el formulario del sitio) |
| `GET /precios?ean=…` | Precios confirmados de un producto, últimos 30 días |
| `GET /exportar.csv` | Todos los precios confirmados |
| `GET /admin` | Página para moderar los pendientes (pide la clave) |

## Cómo publicarlo (una sola vez)

Necesitás [Node](https://nodejs.org) y una cuenta de Cloudflare. Todo pasa adentro de esta carpeta:

```bash
cd comunidad
npm install
```

**1. Iniciar sesión en Cloudflare.** Abre el navegador para autorizar:

```bash
npx wrangler login
```

**2. Crear la base de datos.** El comando devuelve un `database_id`: copialo en `wrangler.toml`, en lugar de `COMPLETAR_CON_EL_ID_DE_D1`.

```bash
npx wrangler d1 create changuito-comunidad
```

**3. Crear las tablas:**

```bash
npm run crear-tablas
```

**4. Cargar los secretos.** Cada comando pide el valor y no queda escrito en ningún archivo.

```bash
npx wrangler secret put TURNSTILE_SECRET
```

```bash
npx wrangler secret put ADMIN_TOKEN
```

```bash
npx wrangler secret put SAL_IP
```

- `TURNSTILE_SECRET`: la **Secret Key** del widget de Turnstile (panel de Cloudflare → Turnstile).
- `ADMIN_TOKEN`: una clave larga que inventás vos, para entrar a `/admin`.
- `SAL_IP`: cualquier texto largo al azar. Una vez elegido, no lo cambies.

**5. Publicar:**

```bash
npm run deploy
```

Te devuelve una dirección como `https://changuito-comunidad.TU-USUARIO.workers.dev`.

**6. Conectar el sitio.** En `comunidad/sitio.json`, completá:

- `url` con esa dirección.
- `turnstile_site_key` con la **Site Key** (es pública).

Commitealo. Desde la próxima recolección, el formulario del sitio queda activo.

## Probar en tu compu

Hay que crear `comunidad/.dev.vars`, que ya está en `.gitignore`. Usá las claves de prueba que publica Cloudflare para Turnstile, que siempre aceptan:

```
TURNSTILE_SECRET=1x0000000000000000000000000000000AA
ADMIN_TOKEN=clave-de-prueba-local
SAL_IP=sal-de-prueba-local
```

```bash
npx wrangler d1 execute changuito-comunidad --local --file=schema.sql
```

```bash
npx wrangler dev --local --port 8787
```

Y desde la raíz del repo, para generar el sitio apuntando al servidor local:

```bash
CHANGUITO_COMUNIDAD_URL=http://127.0.0.1:8787 CHANGUITO_TURNSTILE_SITE_KEY=1x00000000000000000000AA python -m changuito sitio
```

Tests de las reglas:

```bash
node --test test/reglas.test.js
```
