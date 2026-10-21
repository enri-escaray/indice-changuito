import json

from changuito.canasta import Producto
from changuito.fuentes import coto


def registro(ean, lista, descuentos=(), nombre="Yerba Playadito 1 kg"):
    return {
        "attributes": {
            "product.eanPrincipal": [ean],
            "product.displayName": [nombre],
            "sku.activePrice": [f"{lista:.6f}"],
            "product.dtoDescuentos": [json.dumps(list(descuentos))],
        }
    }


def respuesta(*registros):
    # Endeca anida los productos varios niveles; el parser los busca en cualquier lugar.
    return {"contents": [{"Main": [{"contents": [{"records": [{"records": [r]} for r in registros]}]}]}]}


def test_encuentra_el_producto_por_su_codigo_de_barras():
    datos = respuesta(registro("111", 900, nombre="Otra"), registro("7793704000928", 5190))
    precio = coto.parsear_busqueda(datos, "7793704000928")
    assert (precio.tienda, precio.ean, precio.precio, precio.precio_lista) == ("coto", "7793704000928", 5190, 5190)


def test_sin_ese_codigo_devuelve_none():
    assert coto.parsear_busqueda(respuesta(registro("111", 900)), "222") is None


def test_descuento_directo_cuenta_como_oferta():
    descuento = {"textoDescuento": "35%Dto", "precioDesc": "2891.19"}
    precio = coto.parsear_busqueda(respuesta(registro("1", 4447.99, [descuento])), "1")
    assert (precio.precio, precio.precio_lista) == (2891.19, 4447.99)


def test_promos_por_cantidad_y_precio_contado_se_ignoran():
    descuentos = [
        {"textoDescuento": "2do al 70%", "precioDesc": "1000"},
        {"textoDescuento": "", "textoPrecioRegular": "Precio Contado:", "precioDesc": "2050.00"},
    ]
    precio = coto.parsear_busqueda(respuesta(registro("1", 2050, descuentos)), "1")
    assert (precio.precio, precio.precio_lista) == (2050, 2050)


def test_sin_precio_valido_se_saltea():
    assert coto.parsear_busqueda(respuesta(registro("1", 0)), "1") is None


def test_consultas_sin_tamanos():
    assert coto.consultas_para("Fideos spaghetti Matarazzo 500 g") == [
        "Fideos spaghetti Matarazzo 500 g",
        "Fideos spaghetti Matarazzo",
    ]
    assert coto.consultas_para("Yerba Playadito") == ["Yerba Playadito"]


class SesionFalsa:
    def __init__(self, respuestas):
        self.respuestas = respuestas
        self.consultas = []

    def get(self, url, params, timeout):
        self.consultas.append(params["Ntt"])
        self._datos = self.respuestas.pop(0)
        return self

    def raise_for_status(self):
        pass

    def json(self):
        return self._datos


def test_si_el_nombre_completo_no_aparece_prueba_el_corto():
    sesion = SesionFalsa([respuesta(), respuesta(registro("7790070336309", 2100))])
    producto = Producto(ean="7790070336309", nombre="Fideos spaghetti Matarazzo 500 g", categoria="pan")
    precios, errores = coto.precios_de_tienda([producto], pausa=0, sesion=sesion)
    assert sesion.consultas == ["Fideos spaghetti Matarazzo 500 g", "Fideos spaghetti Matarazzo"]
    assert [p.precio for p in precios] == [2100] and errores == []
