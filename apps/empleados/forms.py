from django import forms

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
