from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellido", "telefono", "correo", "fecha_registro")
    list_filter = ("fecha_registro",)
    search_fields = ("nombre", "apellido", "telefono", "correo")
    ordering = ("apellido", "nombre")
    list_per_page = 20
    readonly_fields = ('fecha_registro',)

    fieldsets = (
        ("Datos personales", {
            "fields": ("nombre", "apellido", "telefono", "correo")
        }),
        ("Auditoría", {
            "fields": ("fecha_registro",),
            "classes": ("collapse",)
        }),
    )