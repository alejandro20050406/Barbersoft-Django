from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.catalogos.models import MetodoDePago
from apps.empleados.models import Empleado
from apps.ventas.models import Venta, Visita
from .forms import ClienteForm
from .models import Cliente


class ClienteTelefonoValidationTests(SimpleTestCase):
    def test_form_rechaza_apellido_vacio(self):
        form = ClienteForm(
            data={
                "nombre": "Pedro",
                "apellido": "",
                "telefono": "3125467731",
                "correo": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("apellido", form.errors)

    def test_form_rechaza_telefono_vacio(self):
        form = ClienteForm(
            data={
                "nombre": "Pedro",
                "apellido": "Rocha",
                "telefono": "",
                "correo": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("telefono", form.errors)

    def test_form_rechaza_telefono_con_menos_de_10_digitos(self):
        form = ClienteForm(
            data={
                "nombre": "Pedro",
                "apellido": "Rocha",
                "telefono": "3123431",
                "correo": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("telefono", form.errors)

    def test_form_normaliza_telefono_a_10_digitos(self):
        form = ClienteForm(
            data={
                "nombre": "Jose",
                "apellido": "Castellanos",
                "telefono": "(312) 546-7731",
                "correo": "",
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["telefono"], "3125467731")

    def test_model_rechaza_telefono_invalido(self):
        cliente = Cliente(nombre="Pedro", apellido="Rocha", telefono="12345")

        with self.assertRaises(ValidationError):
            cliente.full_clean()

    def test_model_rechaza_telefono_vacio(self):
        cliente = Cliente(nombre="Pedro", apellido="Rocha", telefono="")

        with self.assertRaises(ValidationError):
            cliente.full_clean()

    def test_model_rechaza_apellido_vacio(self):
        cliente = Cliente(nombre="Pedro", apellido="", telefono="3125467731")

        with self.assertRaises(ValidationError):
            cliente.full_clean()


class ClienteUppercasePersistenceTests(TestCase):
    def test_guarda_nombre_y_apellido_en_mayusculas(self):
        cliente = Cliente.objects.create(
            nombre=" Gael ",
            apellido=" Cortes ",
            telefono="3125467731",
        )

        cliente.refresh_from_db()

        self.assertEqual(cliente.nombre, "GAEL")
        self.assertEqual(cliente.apellido, "CORTES")
        self.assertEqual(str(cliente), "GAEL CORTES")

    def test_lista_clientes_muestra_mas_reciente_primero(self):
        primero = Cliente.objects.create(
            nombre="Ana",
            apellido="Lopez",
            telefono="3125467731",
        )
        reciente = Cliente.objects.create(
            nombre="Bruno",
            apellido="Martinez",
            telefono="3125467732",
        )

        self.assertEqual(list(Cliente.objects.all()), [reciente, primero])


class ClienteFrequencyFilterTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="admin",
            password="admin123",
            is_staff=True,
        )
        self.client.force_login(self.user)
        self.empleado = Empleado.objects.create(
            nombre="Luis",
            apellido="Perez",
            telefono="3125467733",
            estado=Empleado.ACTIVO,
        )
        self.metodo = MetodoDePago.objects.create(nombre="Efectivo", activo=True)
        self.cliente_reciente = Cliente.objects.create(
            nombre="Ana",
            apellido="Lopez",
            telefono="3125467734",
        )
        self.cliente_antiguo = Cliente.objects.create(
            nombre="Bruno",
            apellido="Martinez",
            telefono="3125467735",
        )

    def _crear_visita(self, cliente, fecha):
        venta = Venta.objects.create(
            empleado=self.empleado,
            cliente=cliente,
            metodo_de_pago=self.metodo,
            fecha=fecha,
            total=100,
        )
        return Visita.objects.create(
            cliente=cliente,
            empleado=self.empleado,
            venta=venta,
            fecha=fecha,
        )

    def test_filtra_frecuencia_por_ultimo_mes(self):
        today = timezone.localdate()
        self._crear_visita(self.cliente_reciente, today)
        self._crear_visita(self.cliente_antiguo, today.replace(year=today.year - 1))

        response = self.client.get(reverse("clientes:cliente-list"), {"frecuencia": "1"})

        clientes = list(response.context["clientes"])
        self.assertEqual(clientes, [self.cliente_reciente])
        self.assertEqual(clientes[0].total_visitas, 1)
        self.assertEqual(response.context["selected_frequency_filter"], "1")


class ClienteDeleteTests(TestCase):
    def test_eliminar_cliente_con_ventas_lo_oculta_del_listado(self):
        user = get_user_model().objects.create_user(
            username="admin-delete",
            password="admin123",
            is_staff=True,
        )
        self.client.force_login(user)
        empleado = Empleado.objects.create(
            nombre="Luis",
            apellido="Perez",
            telefono="3125467733",
            estado=Empleado.ACTIVO,
        )
        metodo = MetodoDePago.objects.create(nombre="Efectivo", activo=True)
        cliente = Cliente.objects.create(
            nombre="Carlos",
            apellido="Luna",
            telefono="3125467734",
        )
        Venta.objects.create(
            empleado=empleado,
            cliente=cliente,
            metodo_de_pago=metodo,
            fecha=timezone.localdate(),
            total=100,
        )

        response = self.client.post(reverse("clientes:cliente-delete", args=[cliente.pk]))
        cliente.refresh_from_db()
        list_response = self.client.get(reverse("clientes:cliente-list"))

        self.assertRedirects(response, reverse("clientes:cliente-list"))
        self.assertFalse(cliente.activo)
        self.assertNotContains(list_response, "CARLOS")


class ClienteCreateFromSaleTests(TestCase):
    def setUp(self):
        employee_group = Group.objects.create(name="Empleado")
        self.user = get_user_model().objects.create_user(
            username="barbero",
            password="admin123",
        )
        self.user.groups.add(employee_group)
        self.client.force_login(self.user)
        self.create_url = reverse("clientes:cliente-create")
        self.sale_url = reverse("ventas:venta-create")

    def test_empleado_crea_cliente_desde_nueva_venta_y_regresa_con_cliente(self):
        response = self.client.get(
            self.create_url,
            {"nombre": "Mario Rossi", "next": self.sale_url},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].initial["nombre"], "Mario Rossi")
        self.assertEqual(response.context["next_url"], self.sale_url)

        response = self.client.post(
            self.create_url,
            data={
                "nombre": "Mario",
                "apellido": "Rossi",
                "telefono": "6621234567",
                "correo": "",
                "next": self.sale_url,
            },
        )

        cliente = Cliente.objects.get(nombre="MARIO")
        self.assertRedirects(response, f"{self.sale_url}?cliente={cliente.pk}")

    def test_empleado_no_entra_a_crear_cliente_sin_regreso_a_venta(self):
        response = self.client.get(self.create_url)

        self.assertRedirects(response, reverse("accounts:menu-empleado"))
