"""Cliente para la API pública de catálogo de las tiendas que usan VTEX.

Carrefour, Día, Jumbo, Disco, Vea y Más Online exponen el mismo endpoint
`/api/catalog_system/pub/products/search`, que permite buscar un producto
por su código de barras (EAN) y devuelve el precio de venta online.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from urllib.parse import quote, urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

TIENDAS: dict[str, str] = {
    "carrefour": "https://www.carrefour.com.ar",
    "dia": "https://diaonline.supermercadosdia.com.ar",
    "jumbo": "https://www.jumbo.com.ar",
    "disco": "https://www.disco.com.ar",
    "vea": "https://www.vea.com.ar",
    "masonline": "https://www.masonline.com.ar",
}

USER_AGENT = "Mozilla/5.0 (compatible; indice-changuito/0.1; medicion de precios open source)"
RUTA_BUSQUEDA = "/api/catalog_system/pub/products/search"


@dataclass(frozen=True)
class Precio:
    tienda: str
    ean: str
    nombre: str
    precio: float  # lo que se paga hoy, con promociones incluidas
    precio_lista: float  # precio regular, sin promociones temporarias


def precio_de_lista(precio: float, lista: float | None) -> float:
    """Precio regular a partir de `Price` y `ListPrice` de VTEX.

    Carrefour, Día y Más Online usan ListPrice para el precio sin promoción.
    Jumbo, Disco y Vea (Cencosud) mandan en ListPrice el precio sin IVA multiplicado
    por 100, que no sirve: en ese caso (o si falta) se usa el precio de venta.
    """
    if lista and precio <= lista <= 3 * precio:
        return float(lista)
    return float(precio)


def nueva_sesion() -> requests.Session:
    """Sesión HTTP con reintentos para errores transitorios y límites de tasa."""
    sesion = requests.Session()
    sesion.headers["User-Agent"] = USER_AGENT
    reintentos = Retry(
        total=3,
        backoff_factor=1.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    sesion.mount("https://", HTTPAdapter(max_retries=reintentos))
    return sesion


def parsear_producto(producto: dict, tienda: str, ean: str | None = None) -> Precio | None:
    """Extrae el precio de un producto de la respuesta de VTEX.

    Si se pasa `ean`, solo considera el SKU con ese código de barras.
    Devuelve None si el producto no tiene stock o no tiene precio válido.
    """
    for item in producto.get("items", []):
        if ean is not None and item.get("ean") != ean:
            continue
        for vendedor in item.get("sellers", []):
            oferta = vendedor.get("commertialOffer") or {}
            precio = oferta.get("Price") or 0
            if oferta.get("IsAvailable") and precio > 0:
                return Precio(
                    tienda=tienda,
                    ean=item.get("ean") or "",
                    nombre=producto.get("productName", "").strip(),
                    precio=float(precio),
                    precio_lista=precio_de_lista(precio, oferta.get("ListPrice")),
                )
    return None


def _buscar(sesion: requests.Session, tienda: str, params: dict) -> list[dict]:
    # VTEX rechaza con 400 los espacios codificados como "+": hay que mandarlos como %20.
    consulta = urlencode(params, quote_via=quote)
    respuesta = sesion.get(f"{TIENDAS[tienda]}{RUTA_BUSQUEDA}?{consulta}", timeout=30)
    # VTEX responde 206 (Partial Content) cuando hay más resultados que el rango pedido.
    if respuesta.status_code not in (200, 206):
        respuesta.raise_for_status()
    return respuesta.json()


def precio_por_ean(sesion: requests.Session, tienda: str, ean: str) -> Precio | None:
    """Busca un producto por código de barras en una tienda."""
    for producto in _buscar(sesion, tienda, {"fq": f"alternateIds_Ean:{ean}"}):
        precio = parsear_producto(producto, tienda, ean)
        if precio is not None:
            return precio
    return None


def buscar_texto(sesion: requests.Session, tienda: str, texto: str, cantidad: int = 10) -> list[Precio]:
    """Búsqueda libre, útil para encontrar el EAN de un producto al armar la canasta."""
    productos = _buscar(sesion, tienda, {"ft": texto, "_from": 0, "_to": cantidad - 1})
    resultados = (parsear_producto(p, tienda) for p in productos)
    return [r for r in resultados if r is not None]


def precios_de_tienda(
    tienda: str, eans: list[str], pausa: float = 0.3, sesion: requests.Session | None = None
) -> tuple[list[Precio], list[str]]:
    """Consulta todos los EAN en una tienda, de a uno y con una pausa entre pedidos.

    Devuelve los precios encontrados y la lista de EAN que fallaron por error de red.
    """
    sesion = sesion or nueva_sesion()
    precios: list[Precio] = []
    errores: list[str] = []
    for ean in eans:
        try:
            precio = precio_por_ean(sesion, tienda, ean)
        except (requests.RequestException, ValueError):
            errores.append(ean)
        else:
            if precio is not None:
                precios.append(precio)
        time.sleep(pausa)
    return precios, errores
