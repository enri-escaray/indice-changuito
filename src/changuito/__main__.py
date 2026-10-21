"""Línea de comandos: python -m changuito <comando>."""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from changuito import indice, recolectar, sitio
from changuito.canasta import cargar_canasta
from changuito.fuentes import vtex

# Argentina no tiene horario de verano: UTC-3 todo el año.
HORA_ARGENTINA = timezone(timedelta(hours=-3))


def hoy() -> date:
    return datetime.now(HORA_ARGENTINA).date()


def cmd_recolectar(args: argparse.Namespace) -> int:
    canasta = cargar_canasta(args.canasta)
    fecha = date.fromisoformat(args.fecha) if args.fecha else hoy()
    print(f"Recolectando {len(canasta.eans)} productos en {len(args.tiendas)} tiendas ({fecha})...")
    resultado = recolectar.recolectar(canasta, fecha, args.tiendas, pausa=args.pausa)
    por_tienda = resultado.cantidad_por_tienda()
    for tienda in args.tiendas:
        errores = len(resultado.errores.get(tienda, []))
        aviso = f"  ({errores} errores de red)" if errores else ""
        print(f"  {tienda:10} {por_tienda.get(tienda, 0):3}/{len(canasta.eans)} precios{aviso}")
    if not resultado.filas:
        print("No se obtuvo ningún precio: no se guarda nada.", file=sys.stderr)
        return 1
    ruta = recolectar.guardar(resultado, args.datos / "precios")
    print(f"Guardado en {ruta}")
    return 0


def cmd_calcular(args: argparse.Namespace) -> int:
    canasta = cargar_canasta(args.canasta)
    resultado = indice.calcular(indice.cargar_precios(args.datos / "precios"), canasta)
    indice.guardar(resultado, args.datos)
    ultimo = resultado.diario.iloc[-1]
    print(f"Índice general al {resultado.diario.index[-1]:%Y-%m-%d}: {ultimo['general']:.2f} (base 100)")
    return 0


def cmd_sitio(args: argparse.Namespace) -> int:
    canasta = cargar_canasta(args.canasta)
    precios = indice.cargar_precios(args.datos / "precios")
    resultado = indice.calcular(precios, canasta)
    ruta = sitio.generar(resultado, precios, canasta, args.salida)
    print(f"Sitio generado en {ruta}")
    return 0


def cmd_actualizar(args: argparse.Namespace) -> int:
    for paso in (cmd_recolectar, cmd_calcular, cmd_sitio):
        if codigo := paso(args):
            return codigo
    return 0


def cmd_buscar(args: argparse.Namespace) -> int:
    resultados = vtex.buscar_texto(vtex.nueva_sesion(), args.tienda, args.texto, args.cantidad)
    if not resultados:
        print("Sin resultados.")
    for r in resultados:
        print(f"{r.ean:14}  ${r.precio:>10,.2f}  {r.nombre}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="changuito", description="Índice de precios de supermercados")
    parser.add_argument("--canasta", type=Path, default=Path("canasta.yaml"))
    parser.add_argument("--datos", type=Path, default=Path("data"))
    parser.add_argument("--salida", type=Path, default=Path("docs"), help="carpeta del sitio estático")
    sub = parser.add_subparsers(dest="comando", required=True)

    def con_opciones_de_recoleccion(p: argparse.ArgumentParser) -> None:
        p.add_argument("--fecha", help="AAAA-MM-DD (por defecto, hoy en Argentina)")
        p.add_argument("--tiendas", nargs="+", choices=recolectar.TIENDAS, default=recolectar.TIENDAS)
        p.add_argument("--pausa", type=float, default=0.3, help="segundos entre pedidos a una tienda")

    con_opciones_de_recoleccion(sub.add_parser("recolectar", help="bajar los precios de hoy"))
    sub.add_parser("calcular", help="recalcular el índice con todos los precios guardados")
    sub.add_parser("sitio", help="generar el sitio estático con los gráficos")
    con_opciones_de_recoleccion(sub.add_parser("actualizar", help="recolectar + calcular + sitio"))

    p_buscar = sub.add_parser("buscar", help="buscar productos para encontrar su EAN")
    p_buscar.add_argument("texto")
    p_buscar.add_argument("--tienda", choices=list(vtex.TIENDAS), default="carrefour")
    p_buscar.add_argument("--cantidad", type=int, default=10)

    args = parser.parse_args(argv)
    comandos = {
        "recolectar": cmd_recolectar,
        "calcular": cmd_calcular,
        "sitio": cmd_sitio,
        "actualizar": cmd_actualizar,
        "buscar": cmd_buscar,
    }
    return comandos[args.comando](args)


if __name__ == "__main__":
    sys.exit(main())
