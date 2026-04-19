from django import forms

from .models import Pago, Venta, VentaDetalleProducto, VentaDetalleServicio


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ["empleado", "cliente", "metodo_de_pago", "fecha", "total"]


class VentaDetalleProductoForm(forms.ModelForm):
    class Meta:
        model = VentaDetalleProducto
        fields = ["venta", "producto", "cantidad", "precio_unitario", "subtotal"]


class VentaDetalleServicioForm(forms.ModelForm):
    class Meta:
        model = VentaDetalleServicio
        fields = ["venta", "servicio", "precio_unitario", "subtotal"]


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ["venta", "metodo_de_pago", "monto", "fecha"]
