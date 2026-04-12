from django.contrib import admin
from .models import (Venta,VentaDetalleProducto,VentaDetalleServicio, Pago,Visita, Comision,)

class VentaDetalleProcutoInline(admin.TabularInline):
    model = VentaDetalleProducto
    extra = 1

class VentaDetalleServicioInline(admin.TabularInline):
    model = VentaDetalleServicio
    extra = 1   

class PagoInline(admin.TabularInline):
    model=Pago
    extra=1

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'empleado', 'cliente', 'fecha', 'total')
    list_filter = ('fecha', 'empleado')
    search_fields = ('cliente__nombre', 'empleado__nombre')
    inlines = [VentaDetalleProcutoInline, VentaDetalleServicioInline, PagoInline]      

@admin.register(Comision)
class ComisionAdmin(admin.ModelAdmin):
    list_display = ['id', 'empleado', 'venta', 'porcentaje', 'monto', 'fecha']
    list_filter = ['fecha', 'empleado']


@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'empleado', 'fecha']
    list_filter = ['fecha']      