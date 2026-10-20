"""Pruebas de punta a punta, sin internet: recolectar -> CSV -> DuckDB -> índice -> sitio."""

import json
import re
from datetime import date

import pytest

from changuito import indice, recolectar, sitio
from changuito.fuentes import vtex


def tienda_falsa(precio_base):
    def precios_de_tienda(tienda, eans, pausa=0.3, sesion=None):
        return [vtex.Precio(tienda, e, f"Producto {e}", precio_base) for e in eans], []

    return precios_de_tienda


def recolectar_dia(monkeypatch, canasta, dir_precios, fecha, precio):
    monkeypatch.setattr(vtex, "precios_de_tienda", tienda_falsa(precio))
    resultado = recolectar.recolectar(canasta, fecha, tiendas=["carrefour", "dia"])
    return recolectar.guardar(resultado, dir_precios)


def test_guarda_un_csv_por_dia(monkeypatch, canasta, tmp_path):
    ruta = recolectar_dia(monkeypatch, canasta, tmp_path, date(2026, 3, 5), 100)
    assert ruta == tmp_path / "2026" / "03" / "2026-03-05.csv"
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    assert lineas[0] == "fecha,tienda,ean,nombre,precio"
    assert len(lineas) == 1 + 2 * 3


def test_duckdb_conserva_los_ean_como_texto(tmp_path):
    ruta = tmp_path / "2026" / "01" / "2026-01-01.csv"
    ruta.parent.mkdir(parents=True)
    ruta.write_text("fecha,tienda,ean,nombre,precio\n2026-01-01,dia,0012345678905,\"Yerba, 1 kg\",10.5\n", encoding="utf-8")
    precios = indice.cargar_precios(tmp_path)
    assert precios.loc[0, "ean"] == "0012345678905"
    assert precios.loc[0, "precio"] == 10.5


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
