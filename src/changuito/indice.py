"""Cálculo del índice de precios.

Método, parecido al que usan los IPC oficiales:

1. Panel de precios de lista: una fila por día relevado y una columna por (producto, tienda).
   Se usa el precio regular y no el de promoción, para que el índice mida inflación y no
   promociones que empiezan y terminan. Si falta un precio, se usa el último observado
   hasta `MAX_IMPUTACION` relevamientos.
2. Relativo diario de cada producto: media geométrica (Jevons) de P_t / P_t-1 entre
   las tiendas que tienen precio los dos días.
3. Índice de cada categoría: media geométrica de los relativos de sus productos,
   encadenada día a día. Base 100 = primer día relevado.
4. Índice general: promedio ponderado (tipo Laspeyres) de los índices de categoría.
5. Inflación mensual: promedio del mes contra promedio del mes anterior, como el INDEC.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from changuito.canasta import Canasta

MAX_IMPUTACION = 7


@dataclass
class Resultado:
    diario: pd.DataFrame  # índice por fecha: columna "general" + una por categoría
    mensual: pd.DataFrame  # formato largo: mes, serie, indice, variacion_pct, dias_relevados
    cobertura: pd.DataFrame  # cantidad de productos con precio, por fecha y tienda


def cargar_precios(dir_precios: Path) -> pd.DataFrame:
    """Lee todos los CSV diarios de una vez con DuckDB.

    Los archivos anteriores al 20/10/2026 no tienen `precio_lista`: queda vacío (NaN).
    """
    columnas = ["fecha", "tienda", "ean", "precio", "precio_lista"]
    if not any(dir_precios.glob("**/*.csv")):
        vacio = pd.DataFrame({c: [] for c in columnas})
        vacio["fecha"] = pd.to_datetime(vacio["fecha"])
        return vacio
    patron = (dir_precios / "**" / "*.csv").as_posix().replace("'", "''")
    precios = duckdb.sql(
        f"""
        SELECT *
        FROM read_csv('{patron}', header = true, union_by_name = true,
                      types = {{'fecha': 'DATE', 'ean': 'VARCHAR', 'precio': 'DOUBLE'}})
        WHERE precio > 0
        """
    ).df()
    if "precio_lista" not in precios:
        precios["precio_lista"] = np.nan
    precios["precio_lista"] = pd.to_numeric(precios["precio_lista"])
    precios["fecha"] = pd.to_datetime(precios["fecha"])
    return precios[columnas]


def panel_de_precios(
    precios: pd.DataFrame, columna: str = "precio_lista", max_imputacion: int = MAX_IMPUTACION
) -> pd.DataFrame:
    panel = precios.pivot_table(
        index="fecha", columns=["ean", "tienda"], values=columna, aggfunc="last"
    ).sort_index()
    return panel.ffill(limit=max_imputacion)


def relativos_por_producto(panel: pd.DataFrame) -> pd.DataFrame:
    """Log de la variación diaria de cada producto (fila = día, columna = EAN).

    Promediar logaritmos y después exponenciar es la media geométrica.
    """
    log_relativos = np.log(panel).diff()
    return log_relativos.T.groupby(level="ean").mean().T


def indices_por_categoria(panel: pd.DataFrame, canasta: Canasta) -> pd.DataFrame:
    relativos = relativos_por_producto(panel)
    categoria_de = canasta.categoria_de
    relativos = relativos.loc[:, relativos.columns.isin(list(categoria_de))]
    por_categoria = relativos.T.groupby(relativos.columns.map(categoria_de)).mean().T
    # Un día sin datos para una categoría cuenta como "sin variación".
    por_categoria = por_categoria.reindex(index=panel.index, columns=list(canasta.pesos)).fillna(0.0)
    return 100 * np.exp(por_categoria.cumsum())


def indice_general(por_categoria: pd.DataFrame, canasta: Canasta) -> pd.Series:
    pesos = pd.Series(canasta.pesos)
    return por_categoria[pesos.index].mul(pesos).sum(axis=1).rename("general")


def resumen_mensual(diario: pd.DataFrame) -> pd.DataFrame:
    meses = diario.index.to_period("M")
    promedio = diario.groupby(meses).mean()
    variacion = promedio.pct_change(fill_method=None) * 100
    dias = diario.groupby(meses).size()

    def a_largo(tabla: pd.DataFrame, columna: str) -> pd.DataFrame:
        return tabla.rename_axis("mes").reset_index().melt(id_vars="mes", var_name="serie", value_name=columna)

    resumen = a_largo(promedio, "indice").merge(a_largo(variacion, "variacion_pct"), on=["mes", "serie"])
    resumen["dias_relevados"] = resumen["mes"].map(dias).astype(int)
    resumen["mes"] = resumen["mes"].astype(str)
    return resumen


def nivel_por_tienda(precios_del_dia: pd.DataFrame, min_tiendas: int = 3) -> pd.Series:
    """Cuánto más cara o barata es cada tienda, en % contra la mediana del mercado.

    Para cada producto que está en al menos `min_tiendas` tiendas, se compara el precio
    de cada tienda con la mediana; después se promedian (geométricamente) esas razones.
    """
    tabla = precios_del_dia.pivot_table(index="ean", columns="tienda", values="precio", aggfunc="last")
    tabla = tabla[tabla.notna().sum(axis=1) >= min_tiendas]
    log_razon = np.log(tabla.div(tabla.median(axis=1), axis=0))
    # Una tienda sin productos comparables queda afuera en vez de figurar con NaN.
    return ((np.exp(log_razon.mean()) - 1) * 100).dropna().sort_values()


def comparacion_productos(precios_del_dia: pd.DataFrame) -> pd.DataFrame:
    """Para cada producto: la tienda más barata, la más cara y la brecha entre ambas."""
    filas = []
    for ean, grupo in precios_del_dia.groupby("ean"):
        barato = grupo.loc[grupo["precio"].idxmin()]
        caro = grupo.loc[grupo["precio"].idxmax()]
        filas.append(
            {
                "ean": ean,
                "tienda_barata": barato["tienda"],
                "precio_min": barato["precio"],
                "tienda_cara": caro["tienda"],
                "precio_max": caro["precio"],
                "brecha_pct": (caro["precio"] / barato["precio"] - 1) * 100,
                "tiendas": len(grupo),
            }
        )
    return pd.DataFrame(filas)


def calcular(precios: pd.DataFrame, canasta: Canasta) -> Resultado:
    precios = precios[precios["ean"].isin(canasta.eans) & precios["precio_lista"].notna()]
    if precios.empty:
        raise ValueError("No hay precios de lista de la canasta para calcular el índice")
    panel = panel_de_precios(precios)
    por_categoria = indices_por_categoria(panel, canasta)
    diario = pd.concat([indice_general(por_categoria, canasta), por_categoria], axis=1)
    diario.index.name = "fecha"
    cobertura = precios.groupby(["fecha", "tienda"]).size().unstack(fill_value=0)
    return Resultado(diario=diario, mensual=resumen_mensual(diario), cobertura=cobertura)


def guardar(resultado: Resultado, dir_datos: Path) -> None:
    dir_datos.mkdir(parents=True, exist_ok=True)
    # Siempre LF: así los CSV no cambian según si se generan en Windows o en Linux.
    resultado.diario.round(4).to_csv(
        dir_datos / "indice_diario.csv", date_format="%Y-%m-%d", lineterminator="\n"
    )
    resultado.mensual.round(4).to_csv(dir_datos / "indice_mensual.csv", index=False, lineterminator="\n")
