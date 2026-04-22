from django.contrib import admin

from .models import Empleado


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellido", "telefono", "correo", "porcentaje_comision", "estado", "fecha_ingreso")
    list_filter = ("estado", "fecha_ingreso", "fecha_registro")
    search_fields = ("nombre", "apellido", "correo", "telefono")
    ordering = ("apellido", "nombre")
    list_per_page = 20
    readonly_fields = ('fecha_registro',)

    fieldsets = (
        ("Datos personales", {
            "fields": ("nombre", "apellido", "telefono", "correo")
        }),
        ("Datos laborales", {
            "fields": ("estado", "porcentaje_comision", "fecha_ingreso")
        }),
        ("Auditoría", {
            "fields": ("fecha_registro",),
            "classes": ("collapse",)
        }),
    )