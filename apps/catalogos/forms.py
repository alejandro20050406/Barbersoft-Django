from django import forms

from .models import CategoriaProducto, MetodoDePago, Producto, Servicio, TipoServicio


class CategoriaProductoForm(forms.ModelForm):
    class Meta:
        model = CategoriaProducto
        fields = ["nombre", "descripcion"]


class MetodoDePagoForm(forms.ModelForm):
    class Meta:
        model = MetodoDePago
        fields = ["nombre", "activo"]


class TipoServicioForm(forms.ModelForm):
    class Meta:
        model = TipoServicio
        fields = ["nombre", "descripcion"]


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "categoria",
            "nombre",
            "descripcion",
            "precio_compra",
            "precio_venta",
            "stock",
            "activo",
        ]


class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ["tipo", "nombre", "descripcion", "precio", "activo"]
