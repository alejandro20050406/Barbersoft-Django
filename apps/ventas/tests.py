from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.catalogos.models import CategoriaProducto, MetodoDePago, Producto, Servicio, TipoServicio
from apps.clientes.models import Cliente
from apps.empleados.models import Empleado

from .forms import VentaDetalleProductoForm, VentaForm
from .models import Comision, Venta


class VentaProductAvailabilityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="admin",
            password="admin123",
            is_staff=True,
        )
        self.client.force_login(self.user)
        self.client.defaults["HTTP_HOST"] = "localhost"

        self.categoria = CategoriaProducto.objects.create(nombre="Pomadas")

    def test_venta_create_context_excludes_products_without_stock(self):
        disponible = Producto.objects.create(
            categoria=self.categoria,
            nombre="Cera mate",
            precio_compra=50,
            precio_venta=80,
            stock=3,
            activo=True,
        )
        Producto.objects.create(
            categoria=self.categoria,
            nombre="Gel fijador",
            precio_compra=40,
            precio_venta=70,
            stock=0,
            activo=True,
        )

        response = self.client.get(reverse("ventas:venta-create"))

        self.assertEqual(response.status_code, 200)
        productos = response.context["productos"]
        self.assertEqual([producto["id"] for producto in productos], [disponible.id])

    def test_venta_detalle_producto_form_excludes_products_without_stock(self):
        disponible = Producto.objects.create(
            categoria=self.categoria,
            nombre="Shampoo",
            precio_compra=60,
            precio_venta=95,
            stock=2,
            activo=True,
        )
        agotado = Producto.objects.create(
            categoria=self.categoria,
            nombre="Acondicionador",
            precio_compra=55,
            precio_venta=90,
            stock=0,
            activo=True,
        )

        form = VentaDetalleProductoForm()

        queryset_ids = list(form.fields["producto"].queryset.values_list("id", flat=True))
        self.assertIn(disponible.id, queryset_ids)
        self.assertNotIn(agotado.id, queryset_ids)

    def test_admin_venta_form_uses_admin_as_employee_placeholder(self):
        form = VentaForm(request_user=self.user)

        self.assertEqual(form.fields["empleado"].empty_label, "admin")

    def test_cliente_search_shows_name_without_phone(self):
        Cliente.objects.create(
            nombre="Carlos",
            apellido="Garcia",
            telefono="3129003457",
        )

        response = self.client.get(
            reverse("ventas:api-clientes-search"),
            {"q": "Carlos"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"][0]["text"], "CARLOS GARCIA")


class VentaServicioCommissionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="admin-servicios",
            password="admin123",
            is_staff=True,
        )
        self.client.force_login(self.user)
        self.client.defaults["HTTP_HOST"] = "localhost"

        self.empleado = Empleado.objects.create(
            nombre="Luis",
            apellido="Perez",
            telefono="6621234567",
            estado=Empleado.ACTIVO,
        )
        self.cliente = Cliente.objects.create(
            nombre="Ana",
            apellido="Lopez",
            telefono="6627654321",
        )
        self.metodo = MetodoDePago.objects.create(nombre="Efectivo", activo=True)
        self.tipo_servicio = TipoServicio.objects.create(nombre="Corte")
        self.servicio = Servicio.objects.create(
            tipo=self.tipo_servicio,
            nombre="Buzz cut",
            precio=150,
            activo=True,
        )

    def test_venta_de_servicio_crea_comision_del_80_por_ciento(self):
        response = self.client.post(
            reverse("ventas:venta-create"),
            data={
                "empleado": self.empleado.id,
                "cliente": self.cliente.id,
                "metodo_de_pago": self.metodo.id,
                "fecha": "2026-04-29",
                "item_type": ["servicio"],
                "item_id": [self.servicio.id],
                "item_quantity": ["1"],
            },
        )

        self.assertEqual(response.status_code, 302)
        venta = Venta.objects.get()
        comision = Comision.objects.get(venta=venta)

        self.assertEqual(venta.total, 150)
        self.assertEqual(comision.porcentaje, 80)
        self.assertEqual(comision.monto, 120)
        self.assertEqual(comision.venta_detalle_servicio.subtotal, 150)

    def test_detalle_muestra_distribucion_de_servicio(self):
        self.client.post(
            reverse("ventas:venta-create"),
            data={
                "empleado": self.empleado.id,
                "cliente": self.cliente.id,
                "metodo_de_pago": self.metodo.id,
                "fecha": "2026-04-29",
                "item_type": ["servicio"],
                "item_id": [self.servicio.id],
                "item_quantity": ["1"],
            },
        )
        venta = Venta.objects.get()

        response = self.client.get(reverse("ventas:venta-detail", kwargs={"pk": venta.pk}))

        self.assertContains(response, "Empleado (80%)")
        self.assertContains(response, "$120.00")
        self.assertContains(response, "Ganancia administrador (20%)")
        self.assertContains(response, "$30.00")

    def test_ticket_pdf_se_consulta_inline_sin_guardarse_en_media(self):
        response = self.client.post(
            reverse("ventas:venta-create"),
            data={
                "empleado": self.empleado.id,
                "cliente": self.cliente.id,
                "metodo_de_pago": self.metodo.id,
                "fecha": "2026-04-29",
                "item_type": ["servicio"],
                "item_id": [self.servicio.id],
                "item_quantity": ["1"],
            },
        )

        self.assertEqual(response.status_code, 302)
        venta = Venta.objects.get()
        self.assertFalse(venta.ticket_pdf)

        with patch("apps.ventas.views.HTML") as html_mock:
            html_mock.return_value.write_pdf.return_value = b"%PDF-1.4 fake ticket"

            ticket_response = self.client.get(
                reverse("ventas:venta-ticket-pdf", kwargs={"pk": venta.pk})
            )

        self.assertEqual(ticket_response.status_code, 200)
        self.assertEqual(ticket_response["Content-Type"], "application/pdf")
        self.assertIn("inline; filename=", ticket_response["Content-Disposition"])
        self.assertEqual(ticket_response.content, b"%PDF-1.4 fake ticket")
