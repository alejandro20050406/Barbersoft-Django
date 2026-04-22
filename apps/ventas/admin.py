from django.contrib import admin
from .models import (
    Venta, VentaDetalleProducto, VentaDetalleServicio, 
    Pago, Visita, Comision,
)


class VentaDetalleProductoInline(admin.TabularInline):
    model = VentaDetalleProducto
    extra = 1
    readonly_fields = ('subtotal',)
    fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')


class VentaDetalleServicioInline(admin.TabularInline):
    model = VentaDetalleServicio
    extra = 1
    readonly_fields = ('subtotal',)
    fields = ('servicio', 'precio_unitario', 'subtotal')


class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1
    fields = ('metodo_de_pago', 'monto', 'fecha')


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'empleado', 'metodo_de_pago', 'fecha', 'total')
    list_filter = ('fecha', 'empleado', 'metodo_de_pago')
    search_fields = ('cliente__nombre', 'cliente__apellido', 'empleado__nombre')
    ordering = ('-fecha',)
    list_per_page = 20
    readonly_fields = ('fecha_registro',)
    
    fieldsets = (
        ('Información de la venta', {
            'fields': ('cliente', 'empleado', 'metodo_de_pago', 'fecha', 'total')
        }),
        ('Auditoría', {
            'fields': ('fecha_registro',),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [VentaDetalleProductoInline, VentaDetalleServicioInline, PagoInline]


@admin.register(VentaDetalleProducto)
class VentaDetalleProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('venta__fecha', 'producto')
    search_fields = ('venta__id', 'producto__nombre')
    list_per_page = 20
    
    fieldsets = (
        ('Información del detalle', {
            'fields': ('venta', 'producto')
        }),
        ('Cantidades y precios', {
            'fields': ('cantidad', 'precio_unitario', 'subtotal')
        }),
    )


@admin.register(VentaDetalleServicio)
class VentaDetalleServicioAdmin(admin.ModelAdmin):
    list_display = ('id', 'venta', 'servicio', 'precio_unitario', 'subtotal')
    list_filter = ('venta__fecha', 'servicio')
    search_fields = ('venta__id', 'servicio__nombre')
    list_per_page = 20
    
    fieldsets = (
        ('Información del detalle', {
            'fields': ('venta', 'servicio')
        }),
        ('Precios', {
            'fields': ('precio_unitario', 'subtotal')
        }),
    )


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'venta', 'metodo_de_pago', 'monto', 'fecha')
    list_filter = ('fecha', 'metodo_de_pago')
    search_fields = ('venta__id', 'venta__cliente__nombre')
    ordering = ('-fecha',)
    list_per_page = 20
    
    fieldsets = (
        ('Información del pago', {
            'fields': ('venta', 'metodo_de_pago', 'monto', 'fecha')
        }),
    )


@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'empleado', 'venta', 'fecha')
    list_filter = ('fecha', 'empleado', 'cliente')
    search_fields = ('cliente__nombre', 'cliente__apellido', 'empleado__nombre')
    ordering = ('-fecha',)
    list_per_page = 20
    readonly_fields = ('venta',)
    
    fieldsets = (
        ('Información de la visita', {
            'fields': ('cliente', 'empleado', 'venta', 'fecha')
        }),
        ('Observaciones', {
            'fields': ('observaciones',)
        }),
    )


@admin.register(Comision)
class ComisionAdmin(admin.ModelAdmin):
    list_display = ('id', 'empleado', 'venta', 'porcentaje', 'monto')
    list_filter = ('empleado', 'venta__fecha')
    search_fields = ('empleado__nombre', 'venta__id')
    list_per_page = 20
    
    fieldsets = (
        ('Información de la comisión', {
            'fields': ('empleado', 'venta', 'venta_detalle_producto', 'venta_detalle_servicio')
        }),
        ('Cálculos', {
            'fields': ('porcentaje', 'monto')
        }),
    )      