"""Pruebas de punta a punta, sin internet: recolectar -> CSV -> DuckDB -> índice -> sitio."""

import json
import re
from datetime import date

import pytest

from changuito import indice, recolectar, sitio
from changuito.fuentes import vtex
from conftest import armar_precios


def tienda_falsa(precio_base):
    def precios_de_tienda(tienda, eans, pausa=0.3, sesion=None):
        return [vtex.Precio(tienda, e, f"Producto {e}", precio_base, precio_base) for e in eans], []

    return precios_de_tienda


def recolectar_dia(monkeypatch, canasta, dir_precios, fecha, precio):
    monkeypatch.setattr(vtex, "precios_de_tienda", tienda_falsa(precio))
    resultado = recolectar.recolectar(canasta, fecha, tiendas=["carrefour", "dia"])
    return recolectar.guardar(resultado, dir_precios)


def test_guarda_un_csv_por_dia(monkeypatch, canasta, tmp_path):
    ruta = recolectar_dia(monkeypatch, canasta, tmp_path, date(2026, 3, 5), 100)
    assert ruta == tmp_path / "2026" / "03" / "2026-03-05.csv"
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    assert lineas[0] == "fecha,tienda,ean,nombre,precio,precio_lista"
    assert len(lineas) == 1 + 2 * 3


def escribir_csv(directorio, fecha, contenido):
    ruta = directorio / fecha[:4] / fecha[5:7] / f"{fecha}.csv"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(contenido, encoding="utf-8")


def test_duckdb_conserva_los_ean_como_texto(tmp_path):
    escribir_csv(
        tmp_path, "2026-01-01",
        "fecha,tienda,ean,nombre,precio,precio_lista\n2026-01-01,dia,0012345678905,\"Yerba, 1 kg\",10.5,12\n",
    )
    precios = indice.cargar_precios(tmp_path)
    assert precios.loc[0, "ean"] == "0012345678905"
    assert precios.loc[0, "precio"] == 10.5
    assert precios.loc[0, "precio_lista"] == 12


def test_lee_csv_viejos_sin_precio_de_lista(tmp_path):
    escribir_csv(tmp_path, "2026-01-01", "fecha,tienda,ean,nombre,precio\n2026-01-01,dia,111,Uno,10\n")
    solo_viejos = indice.cargar_precios(tmp_path)
    assert solo_viejos["precio_lista"].isna().all()

    escribir_csv(
        tmp_path, "2026-01-02", "fecha,tienda,ean,nombre,precio,precio_lista\n2026-01-02,dia,111,Uno,8,10\n"
    )
    mezclados = indice.cargar_precios(tmp_path).sort_values("fecha")
    assert mezclados["precio"].tolist() == [10, 8]
    assert mezclados["precio_lista"].isna().tolist() == [True, False]


def test_de_punta_a_punta(monkeypatch, canasta, tmp_path):
    dir_precios = tmp_path / "precios"
    recolectar_dia(monkeypatch, canasta, dir_precios, date(2026, 1, 15), 100)
    recolectar_dia(monkeypatch, canasta, dir_precios, date(2026, 2, 15), 105)

    precios = indice.cargar_precios(dir_precios)
    resultado = indice.calcular(precios, canasta)
    indice.guardar(resultado, tmp_path)
    assert (tmp_path / "indice_diario.csv").exists()
    assert resultado.diario["general"].iloc[-1] == pytest.approx(105)

    html = sitio.generar(resultado, precios, canasta, tmp_path / "docs").read_text(encoding="utf-8")
    assert "__DATOS__" not in html
    datos = json.loads(re.search(r'<script type="application/json" id="datos">(.*?)</script>', html, re.S).group(1))
    assert datos["destacado"] == {"tipo": "mensual", "valor": 5.0, "mes": "2026-02", "en_curso": True, "dias": 1}
    assert len(datos["productos"]) == 3


def test_primer_dia_muestra_cantidad_de_precios(monkeypatch, canasta, tmp_path):
    recolectar_dia(monkeypatch, canasta, tmp_path / "precios", date(2026, 1, 1), 100)
    precios = indice.cargar_precios(tmp_path / "precios")
    datos = sitio.armar_datos(indice.calcular(precios, canasta), precios, canasta)
    assert datos["destacado"] == {"tipo": "inicio", "valor": 6}
    assert all(p["variacion"] is None for p in datos["productos"])


def test_datos_del_buscador(canasta):
    precios = armar_precios(
        [
            ("2026-01-01", "dia", "111", 100),
            ("2026-01-01", "carrefour", "111", 100),
            ("2026-01-02", "dia", "111", 90, 120),  # en promo: lista 120, se paga 90
            ("2026-01-02", "carrefour", "111", 110),
            ("2026-01-02", "jumbo", "333", 50),
        ]
    )
    datos = sitio.armar_datos(indice.calcular(precios, canasta), precios, canasta)
    assert [c["id"] for c in datos["categorias"]] == ["a", "b"]
    assert datos["promos_hoy"] == 1

    leche, tres = datos["productos"]
    assert leche["categoria"] == "a"
    assert leche["precios"] == [
        {"tienda": "Día", "precio": 90.0, "lista": 120.0},
        {"tienda": "Carrefour", "precio": 110.0, "lista": 110.0},
    ]
    assert (leche["barata"], leche["cara"]) == ("Día", "Carrefour")
    # Aumento con precio de lista: media geométrica de +20 % y +10 %.
    assert leche["variacion"] == pytest.approx(((1.2 * 1.1) ** 0.5 - 1) * 100, abs=0.01)
    assert tres["tiendas"] == 1 and tres["variacion"] == 0
