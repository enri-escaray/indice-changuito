"""Carga y validación de la canasta (canasta.yaml)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


class CanastaInvalida(ValueError):
    pass


@dataclass(frozen=True)
class Producto:
    ean: str
    nombre: str
    categoria: str


@dataclass(frozen=True)
class Categoria:
    id: str
    nombre: str
    peso: float  # normalizado: los pesos de todas las categorías suman 1
    productos: tuple[Producto, ...]


@dataclass(frozen=True)
class Canasta:
    categorias: tuple[Categoria, ...]

    @property
    def productos(self) -> list[Producto]:
        return [p for c in self.categorias for p in c.productos]

    @property
    def eans(self) -> list[str]:
        return [p.ean for p in self.productos]

    @property
    def categoria_de(self) -> dict[str, str]:
        return {p.ean: p.categoria for p in self.productos}

    @property
    def pesos(self) -> dict[str, float]:
        return {c.id: c.peso for c in self.categorias}


def desde_dict(datos: dict) -> Canasta:
    crudas = datos.get("categorias") or []
    if not crudas:
        raise CanastaInvalida("La canasta no tiene categorías")

    peso_total = 0.0
    ids: set[str] = set()
    eans: set[str] = set()
    for cat in crudas:
        if cat["id"] in ids:
            raise CanastaInvalida(f"Categoría repetida: {cat['id']}")
        ids.add(cat["id"])
        if not cat.get("peso") or cat["peso"] <= 0:
            raise CanastaInvalida(f"La categoría {cat['id']} necesita un peso positivo")
        if not cat.get("productos"):
            raise CanastaInvalida(f"La categoría {cat['id']} no tiene productos")
        peso_total += cat["peso"]
        for prod in cat["productos"]:
            ean = str(prod["ean"])
            if not ean.isdigit():
                raise CanastaInvalida(f"EAN inválido en {cat['id']}: {ean!r}")
            if ean in eans:
                raise CanastaInvalida(f"EAN repetido: {ean}")
            eans.add(ean)

    return Canasta(
        categorias=tuple(
            Categoria(
                id=cat["id"],
                nombre=cat["nombre"],
                peso=cat["peso"] / peso_total,
                productos=tuple(
                    Producto(ean=str(p["ean"]), nombre=p["nombre"], categoria=cat["id"])
                    for p in cat["productos"]
                ),
            )
            for cat in crudas
        )
    )


def cargar_canasta(ruta: Path) -> Canasta:
    with open(ruta, encoding="utf-8") as f:
        return desde_dict(yaml.safe_load(f))
