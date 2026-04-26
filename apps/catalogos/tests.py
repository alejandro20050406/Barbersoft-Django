from django.test import TestCase

from .models import CategoriaProducto, MetodoDePago, Producto, Servicio, TipoServicio


class CatalogosUppercasePersistenceTests(TestCase):
    def test_guarda_nombres_de_catalogos_en_mayusculas(self):
        categoria = CategoriaProducto.objects.create(nombre=" cabellos ")
        tipo = TipoServicio.objects.create(nombre=" corte ")
        metodo = MetodoDePago.objects.create(nombre=" efectivo ")
        producto = Producto.objects.create(
            categoria=categoria,
            nombre=" pomada ",
            precio_compra=10,
            precio_venta=20,
            stock=5,
        )
        servicio = Servicio.objects.create(tipo=tipo, nombre=" fade ", precio=120)

        for record in [categoria, tipo, metodo, producto, servicio]:
            record.refresh_from_db()

        self.assertEqual(categoria.nombre, "CABELLOS")
        self.assertEqual(tipo.nombre, "CORTE")
        self.assertEqual(metodo.nombre, "EFECTIVO")
        self.assertEqual(producto.nombre, "POMADA")
        self.assertEqual(servicio.nombre, "FADE")
