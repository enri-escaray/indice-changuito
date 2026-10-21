"""Recolección diaria: consulta la canasta en cada tienda y guarda un CSV por día."""

from __future__ import annotations

import csv
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from changuito.canasta import Canasta
from changuito.fuentes import coto, vtex

# Todas las tiendas que se relevan: las VTEX (por código de barras) y Coto (por nombre + código).
TIENDAS = [*vtex.TIENDAS, coto.TIENDA]

COLUMNAS = ("fecha", "tienda", "ean", "nombre", "precio", "precio_lista")


@dataclass
class Recoleccion:
    fecha: date
    filas: list[dict] = field(default_factory=list)
    errores: dict[str, list[str]] = field(default_factory=dict)

    def cantidad_por_tienda(self) -> dict[str, int]:
        cuenta: dict[str, int] = {}
        for fila in self.filas:
            cuenta[fila["tienda"]] = cuenta.get(fila["tienda"], 0) + 1
        return cuenta


def recolectar(
    canasta: Canasta, fecha: date, tiendas: list[str] | None = None, pausa: float = 0.3
) -> Recoleccion:
    """Consulta todas las tiendas en paralelo (pero cada tienda de a un pedido por vez)."""
    tiendas = tiendas or TIENDAS

    def consultar(tienda: str):
        if tienda == coto.TIENDA:
            return coto.precios_de_tienda(canasta.productos, pausa=pausa)
        return vtex.precios_de_tienda(tienda, eans=canasta.eans, pausa=pausa)

    resultado = Recoleccion(fecha=fecha)
    with ThreadPoolExecutor(max_workers=len(tiendas)) as ejecutor:
        for tienda, (precios, errores) in zip(tiendas, ejecutor.map(consultar, tiendas)):
            if errores:
                resultado.errores[tienda] = errores
            resultado.filas.extend(
                {
                    "fecha": fecha.isoformat(),
                    "tienda": p.tienda,
                    "ean": p.ean,
                    "nombre": p.nombre,
                    "precio": p.precio,
                    "precio_lista": p.precio_lista,
                }
                for p in precios
            )
    resultado.filas.sort(key=lambda f: (f["tienda"], f["ean"]))
    return resultado


def ruta_del_dia(dir_precios: Path, fecha: date) -> Path:
    return dir_precios / f"{fecha:%Y}" / f"{fecha:%m}" / f"{fecha.isoformat()}.csv"


def guardar(recoleccion: Recoleccion, dir_precios: Path) -> Path:
    ruta = ruta_del_dia(dir_precios, recoleccion.fecha)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUMNAS, lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(recoleccion.filas)
    return ruta
