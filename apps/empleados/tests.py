from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from .forms import EmpleadoForm
from .models import Empleado


class EmpleadoTelefonoValidationTests(SimpleTestCase):
    def test_form_rechaza_telefono_con_menos_de_10_digitos(self):
        form = EmpleadoForm(
            data={
                "nombre": "Pedro",
                "apellido": "Rocha",
                "telefono": "3123431",
                "correo": "",
                "estado": "activo",
                "fecha_ingreso": "2026-04-23",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("telefono", form.errors)

    def test_form_normaliza_telefono_a_10_digitos(self):
        form = EmpleadoForm(
            data={
                "nombre": "Jose",
                "apellido": "Castellanos",
                "telefono": "312-887-9000",
                "correo": "",
                "estado": "activo",
                "fecha_ingreso": "2026-04-23",
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["telefono"], "3128879000")

    def test_model_rechaza_telefono_invalido(self):
        empleado = Empleado(nombre="Pedro", apellido="Rocha", telefono="12345")

        with self.assertRaises(ValidationError):
            empleado.full_clean()
