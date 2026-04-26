from datetime import date

from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.test import TestCase

from .forms import EmpleadoForm
from .models import Empleado


class EmpleadoTelefonoValidationTests(TestCase):
    def _form_data(self, **overrides):
        data = {
            "nombre": "Pedro",
            "apellido": "Rocha",
            "telefono": "3123431987",
            "correo": "pedro@example.com",
            "estado": "activo",
            "fecha_ingreso": "2026-04-23",
            "username": "pedro_rocha",
            "password": "MesaAzul742!",
        }
        data.update(overrides)
        return data

    def test_form_rechaza_telefono_vacio(self):
        form = EmpleadoForm(data=self._form_data(telefono=""))

        self.assertFalse(form.is_valid())
        self.assertIn("telefono", form.errors)

    def test_form_rechaza_telefono_con_menos_de_10_digitos(self):
        form = EmpleadoForm(data=self._form_data(telefono="3123431"))

        self.assertFalse(form.is_valid())
        self.assertIn("telefono", form.errors)

    def test_form_normaliza_telefono_a_10_digitos(self):
        form = EmpleadoForm(data=self._form_data(telefono="312-887-9000"))

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["telefono"], "3128879000")

    def test_form_rechaza_password_menor_a_8_caracteres(self):
        form = EmpleadoForm(data=self._form_data(password="abc1234"))

        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)

    def test_form_rechaza_password_comun(self):
        form = EmpleadoForm(data=self._form_data(password="password123"))

        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)

    def test_model_rechaza_telefono_invalido(self):
        empleado = Empleado(nombre="Pedro", apellido="Rocha", telefono="12345")

        with self.assertRaises(ValidationError):
            empleado.full_clean()

    def test_model_rechaza_telefono_vacio(self):
        empleado = Empleado(nombre="Pedro", apellido="Rocha", telefono="")

        with self.assertRaises(ValidationError):
            empleado.full_clean()

    def test_guarda_nombre_y_apellido_en_mayusculas(self):
        empleado = Empleado.objects.create(
            nombre=" Rafael ",
            apellido=" Nadal ",
            telefono="3123431987",
            estado=Empleado.ACTIVO,
            fecha_ingreso=date(2026, 4, 23),
        )

        empleado.refresh_from_db()

        self.assertEqual(empleado.nombre, "RAFAEL")
        self.assertEqual(empleado.apellido, "NADAL")
        self.assertEqual(str(empleado), "RAFAEL NADAL")


class EmpleadoCuentaAccesoTests(TestCase):
    def test_form_muestra_fecha_ingreso_al_editar(self):
        empleado = Empleado(
            nombre="Adrian",
            apellido="Aldana",
            telefono="3121345918",
            correo="adrian@example.com",
            estado=Empleado.ACTIVO,
            fecha_ingreso=date(2026, 4, 23),
        )

        form = EmpleadoForm(instance=empleado)

        self.assertIn('value="2026-04-23"', str(form["fecha_ingreso"]))

    def test_form_crea_usuario_para_empleado_existente(self):
        empleado = Empleado.objects.create(
            nombre="Adrian",
            apellido="Aldana",
            telefono="3121345918",
            correo="adrian@example.com",
            estado=Empleado.ACTIVO,
            fecha_ingreso=date(2026, 4, 23),
        )
        form = EmpleadoForm(
            data={
                "nombre": "Adrian",
                "apellido": "Aldana",
                "telefono": "3121345918",
                "correo": "adrian@example.com",
                "estado": Empleado.ACTIVO,
                "fecha_ingreso": "2026-04-23",
                "username": "adrian",
                "password": "MesaAzul742!",
            },
            instance=empleado,
        )

        self.assertTrue(form.is_valid(), form.errors)
        empleado_guardado = form.save()
        empleado_guardado.refresh_from_db()

        self.assertIsNotNone(empleado_guardado.usuario)
        self.assertEqual(empleado_guardado.usuario.username, "adrian")
        self.assertEqual(empleado_guardado.usuario.email, "adrian@example.com")
        self.assertTrue(empleado_guardado.usuario.check_password("MesaAzul742!"))
        self.assertTrue(
            empleado_guardado.usuario.groups.filter(name="Empleado").exists()
        )

    def test_form_actualiza_usuario_vinculado_sin_exigir_password(self):
        Group.objects.create(name="Empleado")
        usuario = User.objects.create_user(
            username="adrian",
            password="secret123",
            email="old@example.com",
        )
        empleado = Empleado.objects.create(
            nombre="Adrian",
            apellido="Aldana",
            telefono="3121345918",
            correo="adrian@example.com",
            estado=Empleado.ACTIVO,
            fecha_ingreso=date(2026, 4, 23),
            usuario=usuario,
        )
        form = EmpleadoForm(
            data={
                "nombre": "Adrian",
                "apellido": "Aldana",
                "telefono": "3121345918",
                "correo": "adrian@example.com",
                "estado": Empleado.ACTIVO,
                "fecha_ingreso": "2026-04-23",
                "username": "adrian_nuevo",
                "password": "",
            },
            instance=empleado,
        )

        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        usuario.refresh_from_db()

        self.assertEqual(usuario.username, "adrian_nuevo")
        self.assertEqual(usuario.email, "adrian@example.com")
        self.assertTrue(usuario.check_password("secret123"))
