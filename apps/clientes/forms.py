import re

from django import forms
from django.core.exceptions import ValidationError

from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "apellido", "telefono", "correo"]
        widgets = {
            "nombre":   forms.TextInput(attrs={"class": "form-control"}),
            "apellido": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "placeholder": "312-185-4639"}),
            "correo":   forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "").strip()
        if not nombre:
            raise ValidationError("El nombre no puede estar vacío.")
        if len(nombre) < 2:
            raise ValidationError("El nombre debe tener al menos 2 caracteres.")
        if any(char.isdigit() for char in nombre):
            raise ValidationError("El nombre no puede contener números.")
        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get("apellido", "")
        if not apellido:
            return apellido  # Es opcional
        apellido = apellido.strip()
        if len(apellido) < 2:
            raise ValidationError("El apellido debe tener al menos 2 caracteres.")
        if any(char.isdigit() for char in apellido):
            raise ValidationError("El apellido no puede contener números.")
        return apellido

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono", "")
        if not telefono:
            return telefono  # Es opcional
        telefono = telefono.strip()
        # Solo dígitos, guiones, espacios y paréntesis
        if not re.match(r'^[\d\s\-\(\)\+]{7,20}$', telefono):
            raise ValidationError("Ingresa un número de teléfono válido (ej: 312-185-4639).")
        return telefono

    def clean_correo(self):
        correo = self.cleaned_data.get("correo", "")
        if not correo:
            return correo  # Es opcional
        return correo.strip().lower()