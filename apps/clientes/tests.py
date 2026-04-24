from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

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
