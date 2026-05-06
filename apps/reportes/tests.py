from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.catalogos.models import (
    CategoriaProducto,
    MetodoDePago,
    Producto,
    Servicio,
    TipoServicio,
)
from apps.clientes.models import Cliente
from apps.empleados.models import Empleado
from apps.ventas.models import (
    Comision,
    Pago,
    Venta,
    VentaDetalleProducto,
    VentaDetalleServicio,
)


class CorteCajaDashboardTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="admin",
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
        self.categoria = CategoriaProducto.objects.create(nombre="Pomadas")
        self.producto = Producto.objects.create(
            categoria=self.categoria,
            nombre="Cera mate",
            precio_compra=90,
            precio_venta=150,
            stock=10,
            activo=True,
        )
        self.tipo_servicio = TipoServicio.objects.create(nombre="Corte")
        self.servicio = Servicio.objects.create(
            tipo=self.tipo_servicio,
            nombre="Corte clasico",
            precio=200,
            activo=True,
        )

    def test_corte_de_caja_calcula_ganancia_neta_del_dia(self):
        today = timezone.localdate()
        venta = Venta.objects.create(
            empleado=self.empleado,
            cliente=self.cliente,
            metodo_de_pago=self.metodo,
            fecha=today,
            total=350,
        )
        VentaDetalleProducto.objects.create(
            venta=venta,
            producto=self.producto,
            cantidad=1,
            precio_unitario=150,
            subtotal=150,
        )
        detalle_servicio = VentaDetalleServicio.objects.create(
            venta=venta,
            servicio=self.servicio,
            precio_unitario=200,
            subtotal=200,
        )
        Comision.objects.create(
            empleado=self.empleado,
            venta=venta,
            venta_detalle_servicio=detalle_servicio,
            porcentaje=Decimal("80.00"),
            fecha=today,
        )
        Pago.objects.create(
            venta=venta,
            metodo_de_pago=self.metodo,
            monto=350,
            fecha=today,
        )

        response = self.client.get(reverse("reportes:dashboard"), {"periodo": "dia"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["ingresos_venta"], 350)
        self.assertEqual(response.context["costo_productos"], 90)
        self.assertEqual(response.context["comisiones"], 160)
        self.assertEqual(response.context["ganancia_neta"], 100)
        self.assertContains(response, "Ganancia neta")
        self.assertContains(response, "$100.00")

    def test_periodo_dia_excluye_ventas_anteriores(self):
        old_date = timezone.localdate() - timedelta(days=1)
        Venta.objects.create(
            empleado=self.empleado,
            cliente=self.cliente,
            metodo_de_pago=self.metodo,
            fecha=old_date,
            total=999,
        )

        response = self.client.get(reverse("reportes:dashboard"), {"periodo": "dia"})

        self.assertEqual(response.context["total_ventas"], 0)
        self.assertEqual(response.context["ingresos_venta"], 0)
