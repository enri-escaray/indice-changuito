import pandas as pd
import pytest

from changuito import indice
from conftest import armar_precios


def todos(fecha: str, precio: float, tiendas=("x", "y"), eans=("111", "222", "333")):
    return [(fecha, t, e, precio) for t in tiendas for e in eans]


def test_suba_pareja_del_10_por_ciento(canasta):
    precios = armar_precios(todos("2026-01-01", 100) + todos("2026-01-02", 110))
    diario = indice.calcular(precios, canasta).diario
    assert diario.loc["2026-01-01"].tolist() == pytest.approx([100, 100, 100])
    assert diario.loc["2026-01-02"].tolist() == pytest.approx([110, 110, 110])


def test_promedia_tiendas_con_media_geometrica(canasta):
    # El producto 333 sube 21 % en una tienda y nada en la otra: sqrt(1,21) = 1,10.
    precios = armar_precios(
        [
            ("2026-01-01", "x", "333", 100),
            ("2026-01-01", "y", "333", 100),
            ("2026-01-02", "x", "333", 121),
            ("2026-01-02", "y", "333", 100),
        ]
    )
    diario = indice.calcular(precios, canasta).diario
    assert diario.loc["2026-01-02", "b"] == pytest.approx(110)


def test_pondera_las_categorias(canasta):
    # "a" sube 10 % y "b" no cambia; pesos 3 a 1: 0,75 * 110 + 0,25 * 100 = 107,5
    precios = armar_precios(
        todos("2026-01-01", 100)
        + [(f, t, e, 110) for f in ["2026-01-02"] for t in ("x", "y") for e in ("111", "222")]
        + [("2026-01-02", t, "333", 100) for t in ("x", "y")]
    )
    diario = indice.calcular(precios, canasta).diario
    assert diario.loc["2026-01-02", "general"] == pytest.approx(107.5)


def test_imputa_precios_faltantes_con_el_ultimo_conocido(canasta):
    # La tienda "x" no publica el día 2; el día 3 vuelve 10 % más cara.
    precios = armar_precios(
        [
            ("2026-01-01", "x", "333", 100),
            ("2026-01-03", "x", "333", 110),
            *[(f, "y", "333", 100) for f in ("2026-01-01", "2026-01-02", "2026-01-03")],
        ]
    )
    diario = indice.calcular(precios, canasta).diario
    assert diario.loc["2026-01-02", "b"] == pytest.approx(100)
    assert diario.loc["2026-01-03", "b"] == pytest.approx(100 * 1.1**0.5)


def test_categoria_sin_datos_no_varia(canasta):
    precios = armar_precios(
        [("2026-01-01", "x", "111", 100), ("2026-01-02", "x", "111", 120)]
    )
    diario = indice.calcular(precios, canasta).diario
    assert diario.loc["2026-01-02", "a"] == pytest.approx(120)
    assert diario.loc["2026-01-02", "b"] == pytest.approx(100)


def test_ignora_productos_que_no_estan_en_la_canasta(canasta):
    precios = armar_precios(
        todos("2026-01-01", 100) + todos("2026-01-02", 100) + [("2026-01-01", "x", "999", 1), ("2026-01-02", "x", "999", 50)]
    )
    diario = indice.calcular(precios, canasta).diario
    assert diario["general"].tolist() == pytest.approx([100, 100])


def test_inflacion_mensual_compara_promedios(canasta):
    enero = [p for d in ("2026-01-10", "2026-01-20") for p in todos(d, 100)]
    febrero = [p for d in ("2026-02-10", "2026-02-20") for p in todos(d, 110)]
    mensual = indice.calcular(armar_precios(enero + febrero), canasta).mensual
    general = mensual[mensual["serie"] == "general"].set_index("mes")
    assert pd.isna(general.loc["2026-01", "variacion_pct"])
    assert general.loc["2026-02", "variacion_pct"] == pytest.approx(10)
    assert general.loc["2026-02", "dias_relevados"] == 2


def test_sin_precios_de_la_canasta_falla(canasta):
    with pytest.raises(ValueError):
        indice.calcular(armar_precios([("2026-01-01", "x", "999", 1)]), canasta)


def test_nivel_por_tienda_contra_la_mediana():
    precios = armar_precios(
        [("2026-01-01", "barata", "1", 90), ("2026-01-01", "media", "1", 100), ("2026-01-01", "cara", "1", 110)]
    )
    nivel = indice.nivel_por_tienda(precios)
    assert nivel.to_dict() == pytest.approx({"barata": -10, "media": 0, "cara": 10})
    assert list(nivel.index) == ["barata", "media", "cara"]


def test_nivel_por_tienda_descarta_productos_en_pocas_tiendas():
    precios = armar_precios([("2026-01-01", "x", "1", 50), ("2026-01-01", "y", "1", 100)])
    assert indice.nivel_por_tienda(precios).empty


def test_comparacion_de_productos():
    precios = armar_precios(
        [("2026-01-01", "x", "1", 100), ("2026-01-01", "y", "1", 150), ("2026-01-01", "x", "2", 10)]
    )
    comparacion = indice.comparacion_productos(precios).set_index("ean")
    assert comparacion.loc["1", "tienda_barata"] == "x"
    assert comparacion.loc["1", "tienda_cara"] == "y"
    assert comparacion.loc["1", "brecha_pct"] == pytest.approx(50)
    assert comparacion.loc["2", "tiendas"] == 1
