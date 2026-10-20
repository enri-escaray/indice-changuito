from changuito.fuentes import vtex


def producto(*items, nombre="Leche entera 1 l"):
    return {"productName": nombre, "items": list(items)}


def item(ean, precio=1000.0, disponible=True):
    return {"ean": ean, "sellers": [{"commertialOffer": {"Price": precio, "IsAvailable": disponible}}]}


def test_toma_el_precio_del_sku_con_el_ean_pedido():
    p = producto(item("111", 500), item("222", 900))
    assert vtex.parsear_producto(p, "carrefour", "222") == vtex.Precio("carrefour", "222", "Leche entera 1 l", 900.0)


def test_sin_stock_o_sin_precio_devuelve_none():
    assert vtex.parsear_producto(producto(item("111", disponible=False)), "dia", "111") is None
    assert vtex.parsear_producto(producto(item("111", precio=0)), "dia", "111") is None
    assert vtex.parsear_producto(producto(item("111")), "dia", "999") is None


def test_usa_el_primer_vendedor_con_precio():
    p = producto(
        {
            "ean": "111",
            "sellers": [
                {"commertialOffer": {"Price": 0, "IsAvailable": False}},
                {"commertialOffer": {"Price": 750, "IsAvailable": True}},
            ],
        }
    )
    assert vtex.parsear_producto(p, "vea", "111").precio == 750


class SesionFalsa:
    def __init__(self, respuesta):
        self.respuesta = respuesta
        self.urls = []

    def get(self, url, timeout):
        self.urls.append(url)
        return self

    status_code = 200

    def json(self):
        return self.respuesta

    def raise_for_status(self):
        pass


def test_codifica_espacios_como_porcentaje_20():
    # VTEX responde 400 si los espacios van como "+".
    sesion = SesionFalsa([producto(item("111"))])
    resultados = vtex.buscar_texto(sesion, "carrefour", "leche entera", cantidad=5)
    assert "ft=leche%20entera" in sesion.urls[0]
    assert "+" not in sesion.urls[0]
    assert [r.ean for r in resultados] == ["111"]


def test_precio_por_ean_filtra_por_codigo_de_barras():
    sesion = SesionFalsa([producto(item("111", 1234))])
    assert vtex.precio_por_ean(sesion, "jumbo", "111").precio == 1234
    assert "fq=alternateIds_Ean%3A111" in sesion.urls[0]
