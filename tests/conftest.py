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


def armar_precios(filas: list[tuple[str, str, str, float]]) -> pd.DataFrame:
    """Filas (fecha, tienda, ean, precio) -> DataFrame como el que devuelve cargar_precios."""
    precios = pd.DataFrame(filas, columns=["fecha", "tienda", "ean", "precio"])
    precios["fecha"] = pd.to_datetime(precios["fecha"])
    return precios
