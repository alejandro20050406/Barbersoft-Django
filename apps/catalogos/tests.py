from datetime import date

from django.test import RequestFactory, TestCase
from django.urls import reverse

from apps.clientes.models import Cliente
from apps.empleados.models import Empleado
from apps.ventas.models import Venta, VentaDetalleProducto
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


class CatalogosDeleteTests(TestCase):
    def test_eliminar_producto_con_ventas_lo_oculta_del_listado(self):
        empleado = Empleado.objects.create(
            nombre="Luis",
            apellido="Perez",
            telefono="3125467733",
            estado=Empleado.ACTIVO,
        )
        cliente = Cliente.objects.create(
            nombre="Ana",
            apellido="Lopez",
            telefono="3125467734",
        )
        metodo = MetodoDePago.objects.create(nombre="Efectivo", activo=True)
        categoria = CategoriaProducto.objects.create(nombre="Pomadas")
        producto = Producto.objects.create(
            categoria=categoria,
            nombre="Pomada mate",
            precio_compra=80,
            precio_venta=120,
            stock=7,
        )
        venta = Venta.objects.create(
            empleado=empleado,
            cliente=cliente,
            metodo_de_pago=metodo,
            fecha=date(2026, 4, 23),
            total=120,
        )
        VentaDetalleProducto.objects.create(
            venta=venta,
            producto=producto,
            cantidad=1,
            precio_unitario=120,
            subtotal=120,
        )

        response = self.client.post(reverse("catalogos:producto-delete", args=[producto.pk]))
        producto.refresh_from_db()
        list_response = self.client.get(reverse("catalogos:producto-list"))

        self.assertRedirects(response, reverse("catalogos:producto-list"))
        self.assertFalse(producto.activo)
        self.assertNotContains(list_response, "POMADA MATE")

    def test_eliminar_categoria_con_productos_la_oculta_del_listado(self):
        categoria = CategoriaProducto.objects.create(nombre="Shampoos")
        Producto.objects.create(
            categoria=categoria,
            nombre="Shampoo solido",
            precio_compra=60,
            precio_venta=100,
            stock=5,
        )

        response = self.client.post(reverse("catalogos:categoria-delete", args=[categoria.pk]))
        categoria.refresh_from_db()
        list_response = self.client.get(reverse("catalogos:categoria-list"))

        self.assertRedirects(response, reverse("catalogos:categoria-list"))
        self.assertFalse(categoria.activo)
        self.assertNotContains(list_response, "SHAMPOOS")
