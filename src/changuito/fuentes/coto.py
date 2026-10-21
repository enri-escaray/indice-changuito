"""Cliente para Coto Digital.

Coto no usa VTEX: su buscador (Oracle Endeca) devuelve JSON si se le agrega `format=json`.
No permite buscar por código de barras, así que se busca por el nombre del producto y se
confirma el resultado por su EAN (`product.eanPrincipal`).

Precios:
- `sku.activePrice` es el precio de lista.
- `product.dtoDescuentos` trae las promos. Solo cuenta un descuento directo ("35%Dto");
  las promos por cantidad ("2do al 70%", "2x1") y los descuentos con tarjeta se ignoran,
  igual que en el resto del índice.
"""

from __future__ import annotations

import json
import re
import time
from collections.abc import Iterable, Iterator

import requests

from changuito.fuentes.vtex import Precio, nueva_sesion

TIENDA = "coto"
URL_BUSQUEDA = "https://www.cotodigital.com.ar/sitios/cdigi/browse"
PROMOS_POR_CANTIDAD = ("2do", "2da", "segund", "x2", "2x1", "3x2", "4x3", "lleva")


def _registros(datos) -> Iterator[dict]:
    """Recorre el JSON de Endeca y devuelve los atributos de cada producto."""
    if isinstance(datos, dict):
        atributos = datos.get("attributes")
        if isinstance(atributos, dict) and "product.eanPrincipal" in atributos:
            yield atributos
        for valor in datos.values():
            yield from _registros(valor)
    elif isinstance(datos, list):
        for valor in datos:
            yield from _registros(valor)


def _primero(atributos: dict, clave: str) -> str:
    valor = atributos.get(clave) or [""]
    return (valor[0] if isinstance(valor, list) else valor) or ""


def es_descuento_directo(descuento: dict) -> bool:
    texto = (descuento.get("textoDescuento") or "").lower()
    if any(p in texto for p in PROMOS_POR_CANTIDAD):
        return False
    return bool(re.search(r"\d+\s*%", texto))


def precios_de_registro(atributos: dict) -> tuple[float, float] | None:
    """(precio que se paga hoy, precio de lista) o None si no hay precio."""
    try:
        lista = float(_primero(atributos, "sku.activePrice"))
    except ValueError:
        return None
    if lista <= 0:
        return None
    try:
        descuentos = json.loads(_primero(atributos, "product.dtoDescuentos") or "[]")
    except json.JSONDecodeError:
        descuentos = []
    precio = lista
    for descuento in descuentos:
        if not es_descuento_directo(descuento):
            continue
        try:
            con_descuento = float(descuento.get("precioDesc") or 0)
        except ValueError:
            continue
        if 0 < con_descuento < precio:
            precio = con_descuento
    return round(precio, 2), round(lista, 2)


def parsear_busqueda(datos, ean: str) -> Precio | None:
    for atributos in _registros(datos):
        if _primero(atributos, "product.eanPrincipal") != ean:
            continue
        precios = precios_de_registro(atributos)
        if precios is None:
            continue
        precio, lista = precios
        nombre = " ".join(_primero(atributos, "product.displayName").split())
        return Precio(tienda=TIENDA, ean=ean, nombre=nombre, precio=precio, precio_lista=lista)
    return None


def consultas_para(nombre: str) -> list[str]:
    """Primero el nombre completo; si no aparece, una versión corta sin tamaños."""
    corto = re.sub(r"\b\d+([.,]\d+)?\s*(g|kg|ml|l|cc|x\d+)\b|\bx\d+\b", " ", nombre, flags=re.IGNORECASE)
    corto = " ".join(corto.split()[:4])
    return list(dict.fromkeys([nombre, corto]))


def _buscar(sesion: requests.Session, texto: str):
    respuesta = sesion.get(URL_BUSQUEDA, params={"Ntt": texto, "format": "json"}, timeout=40)
    respuesta.raise_for_status()
    return respuesta.json()


def precio_por_producto(sesion: requests.Session, ean: str, nombre: str) -> Precio | None:
    for consulta in consultas_para(nombre):
        precio = parsear_busqueda(_buscar(sesion, consulta), ean)
        if precio is not None:
            return precio
    return None


def precios_de_tienda(
    productos: Iterable, pausa: float = 0.3, sesion: requests.Session | None = None
) -> tuple[list[Precio], list[str]]:
    """Consulta cada producto (con `.ean` y `.nombre`) de a uno, con una pausa entre pedidos."""
    sesion = sesion or nueva_sesion()
    precios: list[Precio] = []
    errores: list[str] = []
    for producto in productos:
        try:
            precio = precio_por_producto(sesion, producto.ean, producto.nombre)
        except (requests.RequestException, ValueError):
            errores.append(producto.ean)
        else:
            if precio is not None:
                precios.append(precio)
        time.sleep(pausa)
    return precios, errores
