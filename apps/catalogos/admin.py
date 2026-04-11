from django.contrib import admin

from .models import CategoriaProducto, MetodoDePago, Producto, Servicio, TipoServicio


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "precio_compra", "precio_venta", "stock", "activo")
    list_filter = ("activo", "categoria")
    search_fields = ("nombre",)
    ordering = ("nombre",)


@admin.register(TipoServicio)
class TipoServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "precio", "activo")
    list_filter = ("activo", "tipo")
    search_fields = ("nombre",)
    ordering = ("nombre",)


@admin.register(MetodoDePago)
class MetodoDePagoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre",)