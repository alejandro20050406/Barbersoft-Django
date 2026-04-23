from django import forms

from .models import Pago, Venta, VentaDetalleProducto, VentaDetalleServicio, Visita, Comision


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ["empleado", "cliente", "metodo_de_pago", "fecha", "total"]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'total': forms.NumberInput(attrs={'step': '0.01'}),
        }


class VentaDetalleProductoForm(forms.ModelForm):
    class Meta:
        model = VentaDetalleProducto
        fields = ["venta", "producto", "cantidad", "precio_unitario", "subtotal"]
        widgets = {
            'precio_unitario': forms.NumberInput(attrs={'step': '0.01'}),
            'subtotal': forms.NumberInput(attrs={'step': '0.01'}),
        }


class VentaDetalleServicioForm(forms.ModelForm):
    class Meta:
        model = VentaDetalleServicio
        fields = ["venta", "servicio", "precio_unitario", "subtotal"]
        widgets = {
            'precio_unitario': forms.NumberInput(attrs={'step': '0.01'}),
            'subtotal': forms.NumberInput(attrs={'step': '0.01'}),
        }


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ["venta", "metodo_de_pago", "monto", "fecha"]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'monto': forms.NumberInput(attrs={'step': '0.01'}),
        }


class VisitaForm(forms.ModelForm):
    class Meta:
        model = Visita
        fields = ["cliente", "empleado", "venta", "fecha", "observaciones"]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 4}),
        }


class ComisionForm(forms.ModelForm):
    class Meta:
        model = Comision
        fields = ["empleado", "venta", "venta_detalle_producto", "venta_detalle_servicio", "porcentaje"]
        widgets = {
            'porcentaje': forms.NumberInput(attrs={'step': '0.01'}),
        }
