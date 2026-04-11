from django.contrib import admin

from .models import Empleado


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellido", "telefono", "correo", "porcentaje_comision", "estado")
    list_filter = ("estado",)
    search_fields = ("nombre", "apellido", "correo")
    ordering = ("apellido", "nombre")