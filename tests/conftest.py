import pandas as pd
import pytest

from changuito.canasta import desde_dict


@pytest.fixture
def canasta():
    """Dos categorías: "a" (pesa 3) con dos productos y "b" (pesa 1) con uno."""
    return desde_dict(
        {
            "categorias": [
                {
                    "id": "a",
                    "nombre": "Categoría A",
                    "peso": 3,
                    "productos": [{"ean": "111", "nombre": "Uno"}, {"ean": "222", "nombre": "Dos"}],
                },
                {"id": "b", "nombre": "Categoría B", "peso": 1, "productos": [{"ean": "333", "nombre": "Tres"}]},
            ]
        }
    )


def armar_precios(filas: list[tuple]) -> pd.DataFrame:
    """Filas (fecha, tienda, ean, precio[, precio_lista]) -> DataFrame como el de cargar_precios.

    Si no se da el precio de lista, se usa el mismo precio (producto sin promoción).
    """
    filas = [f if len(f) == 5 else (*f, f[3]) for f in filas]
    precios = pd.DataFrame(filas, columns=["fecha", "tienda", "ean", "precio", "precio_lista"])
    precios["fecha"] = pd.to_datetime(precios["fecha"])
    return precios
