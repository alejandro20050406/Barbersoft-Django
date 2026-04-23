import re

from django import forms
from django.core.exceptions import ValidationError

from .models import Empleado


class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = [
            "nombre",
            "apellido",
            "telefono",
            "correo",
            "porcentaje_comision",
            "estado",
            "fecha_ingreso",
        ]
        widgets = {
            "nombre":               forms.TextInput(attrs={"class": "form-control"}),
            "apellido":             forms.TextInput(attrs={"class": "form-control"}),
            "telefono":             forms.TextInput(attrs={"class": "form-control", "placeholder": "312-185-4639"}),
            "correo":               forms.EmailInput(attrs={"class": "form-control"}),
            "porcentaje_comision":  forms.NumberInput(attrs={"class": "form-control", "min": "0", "max": "100", "step": "0.01"}),
            "estado":               forms.Select(attrs={"class": "form-select"}),
            "fecha_ingreso":        forms.DateInput(attrs={"class": "form-control", "type": "date"}),
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
        apellido = self.cleaned_data.get("apellido", "").strip()
        if not apellido:
            raise ValidationError("El apellido es obligatorio.")
        if len(apellido) < 2:
            raise ValidationError("El apellido debe tener al menos 2 caracteres.")
        if any(char.isdigit() for char in apellido):
            raise ValidationError("El apellido no puede contener números.")
        return apellido

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono", "")
        if not telefono:
            return telefono  # opcional
        telefono = telefono.strip()
        if not re.match(r'^[\d\s\-\(\)\+]{7,20}$', telefono):
            raise ValidationError("Ingresa un número de teléfono válido (ej: 312-185-4639).")
        return telefono

    def clean_correo(self):
        correo = self.cleaned_data.get("correo", "")
        if not correo:
            return correo  # opcional
        return correo.strip().lower()

    def clean_porcentaje_comision(self):
        porcentaje = self.cleaned_data.get("porcentaje_comision")
        if porcentaje is None:
            raise ValidationError("El porcentaje de comisión es obligatorio.")
        if porcentaje < 0:
            raise ValidationError("El porcentaje no puede ser negativo.")
        if porcentaje > 100:
            raise ValidationError("El porcentaje no puede ser mayor a 100.")
        return porcentaje