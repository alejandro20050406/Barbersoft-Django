import re

from django import forms
from django.core.exceptions import ValidationError

from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "apellido", "telefono", "correo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "apellido": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "3121234567",
                    "maxlength": "10",
                    "minlength": "10",
                    "inputmode": "numeric",
                    "pattern": r"\d{10}",
                    "title": "Ingresa exactamente 10 dígitos",
                }
            ),
            "correo": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["apellido"].required = True
        self.fields["apellido"].widget.attrs["required"] = "required"
        self.fields["telefono"].required = True
        self.fields["telefono"].widget.attrs["required"] = "required"

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "").strip()
        if not nombre:
            raise ValidationError("El nombre no puede estar vacío.")
        if len(nombre) < 2:
            raise ValidationError("El nombre debe tener al menos 2 caracteres.")
        if any(char.isdigit() for char in nombre):
            raise ValidationError("El nombre no puede contener números.")
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+$", nombre):
            raise ValidationError(
                "El nombre solo puede contener letras y espacios, sin signos especiales."
            )
        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get("apellido", "").strip()
        if not apellido:
            raise ValidationError("El apellido es obligatorio.")
        if len(apellido) < 2:
            raise ValidationError("El apellido debe tener al menos 2 caracteres.")
        if any(char.isdigit() for char in apellido):
            raise ValidationError("El apellido no puede contener números.")
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+$", apellido):
            raise ValidationError(
                "El apellido solo puede contener letras y espacios, sin signos especiales."
            )
        return apellido

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono", "")
        if not telefono:
            raise ValidationError("El teléfono es obligatorio.")

        telefono_limpio = re.sub(r"\D", "", telefono.strip())
        if len(telefono_limpio) != 10:
            raise ValidationError("Número de teléfono inválido. Debe tener exactamente 10 dígitos.")
        return telefono_limpio

    def clean_correo(self):
        correo = self.cleaned_data.get("correo", "")
        if not correo:
            return correo  # Es opcional
        return correo.strip().lower()
