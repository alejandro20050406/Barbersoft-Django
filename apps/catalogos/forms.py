from django import forms
from django.core.exceptions import ValidationError

from .models import CategoriaProducto, MetodoDePago, Producto, Servicio, TipoServicio


# ──────────────────────────────────────────────
# Mixin reutilizable: widgets con clase CSS base
# ──────────────────────────────────────────────
class StyledFormMixin:
    """Agrega la clase CSS 'form-control' a todos los campos del formulario."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select")
            else:
                field.widget.attrs.setdefault("class", "form-control")


# ──────────────────────────────────────────────
# CategoriaProducto
# ──────────────────────────────────────────────
class CategoriaProductoForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = CategoriaProducto
        fields = ["nombre", "descripcion"]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "").strip()

        if not nombre:
            raise ValidationError("El nombre no puede estar vacío.")

        if len(nombre) < 2:
            raise ValidationError("El nombre debe tener al menos 2 caracteres.")

        # Detectar duplicados (excluye el objeto actual en edición)
        qs = CategoriaProducto.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe una categoría con ese nombre.")

        return nombre


# ──────────────────────────────────────────────
# Producto
# ──────────────────────────────────────────────
class ProductoForm(StyledFormMixin, forms.ModelForm):
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
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "precio_compra": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "precio_venta": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "stock": forms.NumberInput(attrs={"min": "0"}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "").strip()
        if not nombre:
            raise ValidationError("El nombre del producto no puede estar vacío.")
        if len(nombre) < 2:
            raise ValidationError("El nombre debe tener al menos 2 caracteres.")
        return nombre

    def clean_precio_compra(self):
        precio = self.cleaned_data.get("precio_compra")
        if precio is not None and precio < 0:
            raise ValidationError("El precio de compra no puede ser negativo.")
        return precio

    def clean_precio_venta(self):
        precio = self.cleaned_data.get("precio_venta")
        if precio is None:
            raise ValidationError("El precio de venta es obligatorio.")
        if precio <= 0:
            raise ValidationError("El precio de venta debe ser mayor a cero.")
        return precio

    def clean_stock(self):
        stock = self.cleaned_data.get("stock")
        if stock is not None and stock < 0:
            raise ValidationError("El stock no puede ser negativo.")
        return stock

    def clean(self):
        cleaned_data = super().clean()
        precio_compra = cleaned_data.get("precio_compra")
        precio_venta = cleaned_data.get("precio_venta")

        # Solo validar si ambos campos pasaron su validación individual
        if precio_compra is not None and precio_venta is not None:
            if precio_venta < precio_compra:
                raise ValidationError(
                    "El precio de venta no puede ser menor que el precio de compra."
                )
        return cleaned_data


# ──────────────────────────────────────────────
# TipoServicio
# ──────────────────────────────────────────────
class TipoServicioForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = TipoServicio
        fields = ["nombre", "descripcion"]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "").strip()

        if not nombre:
            raise ValidationError("El nombre no puede estar vacío.")

        if len(nombre) < 2:
            raise ValidationError("El nombre debe tener al menos 2 caracteres.")

        qs = TipoServicio.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe un tipo de servicio con ese nombre.")

        return nombre


# ──────────────────────────────────────────────
# Servicio
# ──────────────────────────────────────────────
class ServicioForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ["tipo", "nombre", "descripcion", "precio", "activo"]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "precio": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "").strip()
        if not nombre:
            raise ValidationError("El nombre del servicio no puede estar vacío.")
        if len(nombre) < 2:
            raise ValidationError("El nombre debe tener al menos 2 caracteres.")
        return nombre

    def clean_precio(self):
        precio = self.cleaned_data.get("precio")
        if precio is None:
            raise ValidationError("El precio es obligatorio.")
        if precio <= 0:
            raise ValidationError("El precio debe ser mayor a cero.")
        return precio


# ──────────────────────────────────────────────
# MetodoDePago
# ──────────────────────────────────────────────
class MetodoDePagoForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = MetodoDePago
        fields = ["nombre", "activo"]

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "").strip()

        if not nombre:
            raise ValidationError("El nombre no puede estar vacío.")

        if len(nombre) < 2:
            raise ValidationError("El nombre debe tener al menos 2 caracteres.")

        qs = MetodoDePago.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe un método de pago con ese nombre.")

        return nombre