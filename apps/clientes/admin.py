from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellido", "telefono", "correo", "fecha_registro")
    search_fields = ("nombre", "apellido", "telefono", "correo")
    ordering = ("apellido", "nombre")
    list_per_page = 20

    fieldsets = (
        ("Datos personales", {
            "fields": ("nombre", "apellido", "telefono", "correo")
        }),
    )