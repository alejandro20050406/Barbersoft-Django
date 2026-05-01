from django.test import RequestFactory, TestCase
from django.urls import reverse

from .models import CategoriaProducto, MetodoDePago, Producto, Servicio, TipoServicio
from .views import dashboard


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


class CatalogosDashboardTests(TestCase):
    def test_muestra_productos_servicios_y_ligas_de_catalogos(self):
        categoria = CategoriaProducto.objects.create(nombre="shampoos")
        tipo = TipoServicio.objects.create(nombre="corte")
        Producto.objects.create(
            categoria=categoria,
            nombre="shampoo",
            precio_compra=80,
            precio_venta=120,
            stock=7,
        )
        Servicio.objects.create(tipo=tipo, nombre="corte clasico", precio=150)

        response = dashboard(RequestFactory().get(reverse("catalogos:dashboard")))
        content = response.content.decode()

        self.assertContains(response, "SHAMPOO")
        self.assertContains(response, "CORTE CLASICO")
        self.assertIn(reverse("catalogos:producto-list"), content)
        self.assertIn(reverse("catalogos:servicio-list"), content)
        self.assertIn(reverse("catalogos:categoria-list"), content)
        self.assertIn(reverse("catalogos:metodopago-list"), content)
        self.assertIn(reverse("catalogos:tiposervicio-list"), content)
