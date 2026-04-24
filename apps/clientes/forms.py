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
                    "title": "Ingresa exactamente 10 digitos",
                }
            ),
            "correo": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "").strip()
        if not nombre:
            raise ValidationError("El nombre no puede estar vacio.")
        if len(nombre) < 2:
            raise ValidationError("El nombre debe tener al menos 2 caracteres.")
        if any(char.isdigit() for char in nombre):
            raise ValidationError("El nombre no puede contener numeros.")
        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get("apellido", "")
        if not apellido:
            return apellido  # Es opcional
        apellido = apellido.strip()
        if len(apellido) < 2:
            raise ValidationError("El apellido debe tener al menos 2 caracteres.")
        if any(char.isdigit() for char in apellido):
            raise ValidationError("El apellido no puede contener numeros.")
        return apellido

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono", "")
        if not telefono:
            return telefono  # Es opcional

        telefono_limpio = re.sub(r"\D", "", telefono.strip())
        if len(telefono_limpio) != 10:
            raise ValidationError("Numero de telefono invalido. Debe tener exactamente 10 digitos.")
        return telefono_limpio

    def clean_correo(self):
        correo = self.cleaned_data.get("correo", "")
        if not correo:
            return correo  # Es opcional
        return correo.strip().lower()
