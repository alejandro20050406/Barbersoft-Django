from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.catalogos.models import CategoriaProducto, Producto

from .forms import VentaDetalleProductoForm


class VentaProductAvailabilityTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="admin",
            password="admin123",
            is_staff=True,
        )
        self.client.force_login(self.user)

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
