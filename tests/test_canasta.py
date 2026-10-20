from pathlib import Path

import pytest

from changuito.canasta import CanastaInvalida, cargar_canasta, desde_dict

RAIZ = Path(__file__).resolve().parents[1]


def test_la_canasta_del_repo_es_valida():
    canasta = cargar_canasta(RAIZ / "canasta.yaml")
    assert sum(canasta.pesos.values()) == pytest.approx(1)
    assert len(canasta.eans) >= 40
    assert all(len(ean) in (8, 12, 13) for ean in canasta.eans)


def test_normaliza_los_pesos(canasta):
    assert canasta.pesos == pytest.approx({"a": 0.75, "b": 0.25})
    assert canasta.categoria_de == {"111": "a", "222": "a", "333": "b"}


def categoria(id_, eans, peso=1):
    return {"id": id_, "nombre": id_, "peso": peso, "productos": [{"ean": e, "nombre": e} for e in eans]}


@pytest.mark.parametrize(
    "datos",
    [
        {"categorias": []},
        {"categorias": [categoria("a", ["1"]), categoria("a", ["2"])]},
        {"categorias": [categoria("a", ["1"]), categoria("b", ["1"])]},
        {"categorias": [categoria("a", ["12x"])]},
        {"categorias": [categoria("a", ["1"], peso=0)]},
        {"categorias": [categoria("a", [])]},
    ],
    ids=["vacia", "categoria-repetida", "ean-repetido", "ean-no-numerico", "peso-cero", "sin-productos"],
)
def test_rechaza_canastas_invalidas(datos):
    with pytest.raises(CanastaInvalida):
        desde_dict(datos)
