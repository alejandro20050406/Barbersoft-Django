from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal

from apps.catalogos.models import MetodoDePago, Producto
from apps.empleados.models import Empleado

from .models import (
    Comision,
    Pago,
    Venta,
    VentaDetalleProducto,
    VentaDetalleServicio,
    Visita,
)


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ["empleado", "cliente", "metodo_de_pago", "fecha"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "metodo_de_pago": forms.RadioSelect(),
        }

    def __init__(self, *args, request_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.request_user = request_user
        self.fields["empleado"].queryset = Empleado.objects.filter(estado=Empleado.ACTIVO)
        self.fields["metodo_de_pago"].queryset = MetodoDePago.objects.filter(activo=True)
        self.fields["metodo_de_pago"].empty_label = None
        if getattr(self.instance, "total", None) is None:
            # El total definitivo se calcula con los items en la vista.
            self.instance.total = Decimal("0.00")

    def clean_empleado(self):
        empleado = self.cleaned_data.get("empleado")
        if empleado is None:
            raise ValidationError("El empleado es obligatorio.")
        if empleado.estado != Empleado.ACTIVO:
            raise ValidationError("Solo puedes registrar ventas con empleados activos.")
        return empleado

    def clean_metodo_de_pago(self):
        metodo = self.cleaned_data.get("metodo_de_pago")
        if metodo is None:
            raise ValidationError("El metodo de pago es obligatorio.")
        if not metodo.activo:
            raise ValidationError("El metodo de pago seleccionado esta inactivo.")
        return metodo


class VentaDetalleProductoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        productos_disponibles = Producto.objects.filter(activo=True, stock__gt=0)

        if self.instance.pk and self.instance.producto_id:
            productos_disponibles = Producto.objects.filter(activo=True).filter(
                pk=self.instance.producto_id
            ) | productos_disponibles

        self.fields["producto"].queryset = productos_disponibles.distinct().order_by("nombre")

    class Meta:
        model = VentaDetalleProducto
        fields = ["venta", "producto", "cantidad", "precio_unitario", "subtotal"]
        widgets = {
            "precio_unitario": forms.NumberInput(attrs={"step": "0.01"}),
            "subtotal": forms.NumberInput(attrs={"step": "0.01"}),
        }

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get("cantidad")
        if cantidad is None or cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a cero.")
        return cantidad


class VentaDetalleServicioForm(forms.ModelForm):
    class Meta:
        model = VentaDetalleServicio
        fields = ["venta", "servicio", "precio_unitario", "subtotal"]
        widgets = {
            "precio_unitario": forms.NumberInput(attrs={"step": "0.01"}),
            "subtotal": forms.NumberInput(attrs={"step": "0.01"}),
        }


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ["venta", "metodo_de_pago", "monto", "fecha"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "monto": forms.NumberInput(attrs={"step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["metodo_de_pago"].queryset = MetodoDePago.objects.filter(activo=True)

    def clean_monto(self):
        monto = self.cleaned_data.get("monto")
        if monto is None or monto <= 0:
            raise ValidationError("El monto debe ser mayor a cero.")
        return monto

    def clean(self):
        cleaned_data = super().clean()
        venta = cleaned_data.get("venta")
        if venta and venta.total == 0:
            raise ValidationError("No puedes registrar pagos sobre una venta cancelada.")
        return cleaned_data


class VisitaForm(forms.ModelForm):
    class Meta:
        model = Visita
        fields = ["cliente", "empleado", "venta", "fecha", "observaciones"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "observaciones": forms.Textarea(attrs={"rows": 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        cliente = cleaned_data.get("cliente")
        empleado = cleaned_data.get("empleado")
        venta = cleaned_data.get("venta")

        if venta is not None:
            if cliente and venta.cliente_id != cliente.id:
                raise ValidationError("El cliente de la visita debe coincidir con la venta.")
            if empleado and venta.empleado_id != empleado.id:
                raise ValidationError("El empleado de la visita debe coincidir con la venta.")

        return cleaned_data


class ComisionForm(forms.ModelForm):
    class Meta:
        model = Comision
        fields = [
            "empleado",
            "venta",
            "venta_detalle_producto",
            "venta_detalle_servicio",
            "porcentaje",
        ]
        widgets = {
            "porcentaje": forms.NumberInput(attrs={"step": "0.01"}),
        }

    def clean_porcentaje(self):
        porcentaje = self.cleaned_data.get("porcentaje")
        if porcentaje is None:
            raise ValidationError("El porcentaje es obligatorio.")
        if porcentaje <= 0 or porcentaje > 100:
            raise ValidationError("El porcentaje debe estar entre 0.01 y 100.")
        return porcentaje

    def clean(self):
        cleaned_data = super().clean()
        detalle_producto = cleaned_data.get("venta_detalle_producto")
        detalle_servicio = cleaned_data.get("venta_detalle_servicio")

        if not detalle_producto and not detalle_servicio:
            raise ValidationError(
                "La comision debe relacionarse con un detalle de producto o de servicio."
            )
        if detalle_producto and detalle_servicio:
            raise ValidationError(
                "La comision no puede tener detalle de producto y servicio al mismo tiempo."
            )

        return cleaned_data
