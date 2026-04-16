from django.contrib import admin

from .models import CategoriaProducto, MetodoDePago, Producto, Servicio, TipoServicio


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)
    ordering = ("nombre",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "precio_compra", "precio_venta", "stock", "activo")
    list_filter = ("activo", "categoria")
    search_fields = ("nombre", "categoria__nombre")
    ordering = ("nombre",)
    list_per_page = 20

    fieldsets = (
        ("Información general", {
            "fields": ("nombre", "categoria", "descripcion", "activo")
        }),
        ("Precios e inventario", {
            "fields": ("precio_compra", "precio_venta", "stock")
        }),
    )


@admin.register(TipoServicio)
class TipoServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)
    ordering = ("nombre",)


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "precio", "activo")
    list_filter = ("activo", "tipo")
    search_fields = ("nombre", "tipo__nombre")
    ordering = ("nombre",)
    list_per_page = 20

    fieldsets = (
        ("Información general", {
            "fields": ("nombre", "tipo", "descripcion", "activo")
        }),
        ("Precio", {
            "fields": ("precio",)
        }),
    )


@admin.register(MetodoDePago)
class MetodoDePagoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre",)
    ordering = ("nombre",)