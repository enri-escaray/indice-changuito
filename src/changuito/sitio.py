"""Genera el sitio estático (docs/index.html) que se publica con GitHub Pages."""

from __future__ import annotations

import json
import math
import os
from importlib import resources
from pathlib import Path

import pandas as pd

from changuito import indice
from changuito.canasta import Canasta

NOMBRES_TIENDAS = {
    "carrefour": "Carrefour",
    "dia": "Día",
    "jumbo": "Jumbo",
    "disco": "Disco",
    "vea": "Vea",
    "masonline": "Más Online",
}

# Si no corre en GitHub Actions, se usa el repo original para los enlaces y la vista previa al compartir.
REPO_POR_DEFECTO = "enri-escaray/indice-changuito"


def repositorio() -> str:
    return os.environ.get("GITHUB_REPOSITORY") or REPO_POR_DEFECTO


def url_sitio(repo: str) -> str:
    """URL de GitHub Pages del repo: usuario.github.io/repo/."""
    usuario, nombre = repo.split("/", 1)
    return f"https://{usuario.lower()}.github.io/{nombre}/"


MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre")


def fecha_larga(fecha) -> str:
    """20 de octubre de 2026."""
    return f"{fecha.day} de {MESES[fecha.month - 1]} de {fecha.year}"


def _limpio(valor):
    """Convierte NaN en None para que el JSON quede válido."""
    if isinstance(valor, float) and math.isnan(valor):
        return None
    return valor


def _redondear(valor: float, decimales: int = 2):
    return _limpio(round(float(valor), decimales))


def armar_datos(resultado: indice.Resultado, precios: pd.DataFrame, canasta: Canasta) -> dict:
    diario = resultado.diario
    ultima_fecha = diario.index[-1]
    precios = precios[precios["ean"].isin(canasta.eans)]
    del_dia = precios[precios["fecha"] == ultima_fecha]
    nombres = {p.ean: p.nombre for p in canasta.productos}
    nombres_categoria = {c.id: c.nombre for c in canasta.categorias}

    mensual = resultado.mensual
    meses = list(dict.fromkeys(mensual["mes"]))
    series_mensuales = [
        {
            "id": serie,
            "nombre": "Índice general" if serie == "general" else nombres_categoria[serie],
            "variaciones": [
                _redondear(v) for v in mensual[mensual["serie"] == serie].set_index("mes").loc[meses, "variacion_pct"]
            ],
        }
        for serie in ["general", *canasta.pesos]
    ]
    dias_por_mes = mensual[mensual["serie"] == "general"].set_index("mes").loc[meses, "dias_relevados"]

    general = mensual[(mensual["serie"] == "general") & mensual["variacion_pct"].notna()]
    if not general.empty:
        fila = general.iloc[-1]
        destacado = {
            "tipo": "mensual",
            "valor": _redondear(fila["variacion_pct"]),
            "mes": fila["mes"],
            "en_curso": fila["mes"] == f"{ultima_fecha:%Y-%m}",
            "dias": int(fila["dias_relevados"]),
        }
    elif len(diario) > 1:
        destacado = {"tipo": "acumulada", "valor": _redondear(diario["general"].iloc[-1] - 100)}
    else:
        destacado = {"tipo": "inicio", "valor": len(del_dia)}

    comparacion = indice.comparacion_productos(del_dia)
    comparacion["orden"] = comparacion["ean"].map({e: i for i, e in enumerate(canasta.eans)})
    precios_por_ean = {ean: grupo.sort_values("precio") for ean, grupo in del_dia.groupby("ean")}
    # Con un solo día todavía no hay variación que mostrar.
    variacion_de = (resultado.por_producto.iloc[-1] - 100).to_dict() if len(diario) > 1 else {}

    return {
        "repositorio": f"https://github.com/{repositorio()}",
        "actualizado": f"{ultima_fecha:%Y-%m-%d}",
        "inicio": f"{diario.index[0]:%Y-%m-%d}",
        "dias": len(diario),
        "productos_canasta": len(canasta.eans),
        "precios_hoy": len(del_dia),
        "promos_hoy": int((del_dia["precio"] < del_dia["precio_lista"] - 0.005).sum()),
        "tiendas_hoy": int(del_dia["tienda"].nunique()),
        "destacado": destacado,
        "serie": [
            {"fecha": f"{fecha:%Y-%m-%d}", "valor": _redondear(valor)} for fecha, valor in diario["general"].items()
        ],
        "categorias": [
            {
                "id": c.id,
                "nombre": c.nombre,
                "productos": len(c.productos),
                "peso": _redondear(c.peso * 100, 1),
                "valor": _redondear(diario[c.id].iloc[-1] - 100),
            }
            for c in canasta.categorias
        ],
        "mensual": {"meses": meses, "dias": [int(d) for d in dias_por_mes], "series": series_mensuales},
        "tiendas": [
            {"nombre": NOMBRES_TIENDAS.get(tienda, tienda), "valor": _redondear(pct)}
            for tienda, pct in indice.nivel_por_tienda(del_dia).items()
        ],
        "productos": [
            {
                "ean": fila.ean,
                "nombre": nombres[fila.ean],
                "categoria": canasta.categoria_de[fila.ean],
                "barata": NOMBRES_TIENDAS.get(fila.tienda_barata, fila.tienda_barata),
                "min": _redondear(fila.precio_min),
                "cara": NOMBRES_TIENDAS.get(fila.tienda_cara, fila.tienda_cara),
                "max": _redondear(fila.precio_max),
                "brecha": _redondear(fila.brecha_pct, 1),
                "tiendas": int(fila.tiendas),
                "variacion": _redondear(variacion_de[fila.ean]) if fila.ean in variacion_de else None,
                "precios": [
                    {
                        "tienda": NOMBRES_TIENDAS.get(p.tienda, p.tienda),
                        "precio": _redondear(p.precio),
                        "lista": _redondear(p.precio_lista),
                    }
                    for p in precios_por_ean[fila.ean].itertuples()
                ],
            }
            for fila in comparacion.sort_values("orden").itertuples()
        ],
    }


def exportar_precios_del_dia(resultado: indice.Resultado, precios: pd.DataFrame, canasta: Canasta, ruta: Path) -> None:
    """CSV con los precios del último día, para descargar directo desde el sitio."""
    ultima_fecha = resultado.diario.index[-1]
    del_dia = precios[(precios["fecha"] == ultima_fecha) & precios["ean"].isin(canasta.eans)]
    productos = {p.ean: p for p in canasta.productos}
    categorias = {c.id: c.nombre for c in canasta.categorias}
    tabla = pd.DataFrame(
        {
            "fecha": del_dia["fecha"].dt.strftime("%Y-%m-%d"),
            "tienda": del_dia["tienda"].map(lambda t: NOMBRES_TIENDAS.get(t, t)),
            "ean": del_dia["ean"],
            "producto": del_dia["ean"].map(lambda e: productos[e].nombre),
            "categoria": del_dia["ean"].map(lambda e: categorias[productos[e].categoria]),
            "precio": del_dia["precio"].round(2),
            "precio_lista": del_dia["precio_lista"].round(2),
        }
    ).sort_values(["categoria", "producto", "tienda"])
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(ruta, index=False, lineterminator="\n")


def generar(resultado: indice.Resultado, precios: pd.DataFrame, canasta: Canasta, dir_salida: Path) -> Path:
    datos = armar_datos(resultado, precios, canasta)
    exportar_precios_del_dia(resultado, precios, canasta, dir_salida / "datos" / "precios-hoy.csv")
    # "<\/" evita que un texto con "</script>" corte el bloque de datos.
    json_datos = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
    plantilla = resources.files("changuito").joinpath("plantilla.html").read_text(encoding="utf-8")
    repo = repositorio()
    # Estos valores van en el HTML fijo (metadatos para compartir y texto sin JavaScript).
    pesos = canasta.pesos
    reemplazos = {
        "__URL_SITIO__": url_sitio(repo),
        "__URL_REPO__": f"https://github.com/{repo}",
        "__N_PRODUCTOS__": str(len(canasta.eans)),
        "__N_CATEGORIAS__": str(len(canasta.categorias)),
        "__PESO_NO_ALIMENTOS__": str(round((pesos.get("limpieza", 0) + pesos.get("higiene", 0)) * 100)),
        "__INICIO__": fecha_larga(resultado.diario.index[0]),
        "__ACTUALIZADO__": fecha_larga(resultado.diario.index[-1]),
    }
    for marca, valor in reemplazos.items():
        plantilla = plantilla.replace(marca, valor)
    dir_salida.mkdir(parents=True, exist_ok=True)
    ruta = dir_salida / "index.html"
    ruta.write_text(plantilla.replace("__DATOS__", json_datos), encoding="utf-8", newline="\n")
    return ruta
