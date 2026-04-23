from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class Venta(models.Model):
    empleado = models.ForeignKey(
        "empleados.Empleado",
        on_delete=models.PROTECT,
        related_name="ventas",
        verbose_name="Empleado",
    )
    cliente = models.ForeignKey(
        "clientes.Cliente",
        on_delete=models.PROTECT,
        related_name="ventas",
        verbose_name="Cliente",
    )
    metodo_de_pago = models.ForeignKey(
        "catalogos.MetodoDePago",
        on_delete=models.PROTECT,
        related_name="ventas",
        verbose_name="Metodo de Pago",
    )
    fecha = models.DateField(verbose_name="Fecha de venta")
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total de la venta",
    )

    class Meta:
        db_table = "ventas"
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Venta #{self.pk} - {self.fecha}"

    def clean(self):
        if self.total is None:
            raise ValidationError({"total": "El total es obligatorio."})
        if self.total < 0:
            raise ValidationError({"total": "El total no puede ser negativo."})


class VentaDetalleProducto(models.Model):
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name="detalles_productos",
        verbose_name="Venta",
    )
    producto = models.ForeignKey(
        "catalogos.Producto",
        on_delete=models.PROTECT,
        related_name="detalles_venta",
        verbose_name="Producto",
    )
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio Unitario",
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Subtotal",
    )

    class Meta:
        db_table = "venta_detalle_producto"
        verbose_name = "Detalle de producto"
        verbose_name_plural = "Detalles de productos"

    def __str__(self):
        return f"Detalle producto #{self.pk} - Venta #{self.venta_id}"

    def clean(self):
        if self.cantidad is None or self.cantidad <= 0:
            raise ValidationError({"cantidad": "La cantidad debe ser mayor a cero."})
        if self.precio_unitario is None or self.precio_unitario <= 0:
            raise ValidationError(
                {"precio_unitario": "El precio unitario debe ser mayor a cero."}
            )
        if self.subtotal is None or self.subtotal <= 0:
            raise ValidationError({"subtotal": "El subtotal debe ser mayor a cero."})

        expected = self.precio_unitario * self.cantidad
        if self.subtotal != expected:
            raise ValidationError(
                {"subtotal": "El subtotal no coincide con precio por cantidad."}
            )


class VentaDetalleServicio(models.Model):
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name="detalles_servicio",
        verbose_name="Venta",
    )
    servicio = models.ForeignKey(
        "catalogos.Servicio",
        on_delete=models.PROTECT,
        related_name="detalles_venta",
        verbose_name="Servicio",
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio unitario",
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Subtotal",
    )

    class Meta:
        db_table = "venta_detalle_servicio"
        verbose_name = "Detalle de servicio"
        verbose_name_plural = "Detalles de servicios"

    def __str__(self):
        return f"Detalle servicio #{self.pk} - Venta #{self.venta_id}"

    def clean(self):
        if self.precio_unitario is None or self.precio_unitario <= 0:
            raise ValidationError(
                {"precio_unitario": "El precio unitario debe ser mayor a cero."}
            )
        if self.subtotal is None or self.subtotal <= 0:
            raise ValidationError({"subtotal": "El subtotal debe ser mayor a cero."})
        if self.subtotal < self.precio_unitario:
            raise ValidationError(
                {"subtotal": "El subtotal no puede ser menor al precio unitario."}
            )


class Pago(models.Model):
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name="pagos",
        verbose_name="Venta",
    )
    metodo_de_pago = models.ForeignKey(
        "catalogos.MetodoDePago",
        on_delete=models.PROTECT,
        related_name="pagos",
        verbose_name="Metodo de pago",
    )
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Monto pagado",
    )
    fecha = models.DateField(verbose_name="Fecha de pago")

    class Meta:
        db_table = "pagos"
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self):
        return f"Pago #{self.pk} - Venta #{self.venta_id}"

    def clean(self):
        if self.monto is None or self.monto <= 0:
            raise ValidationError({"monto": "El monto debe ser mayor a cero."})


class Visita(models.Model):
    cliente = models.ForeignKey(
        "clientes.Cliente",
        on_delete=models.PROTECT,
        related_name="visitas",
        verbose_name="Cliente",
    )
    empleado = models.ForeignKey(
        "empleados.Empleado",
        on_delete=models.PROTECT,
        related_name="visitas",
        verbose_name="Empleado",
    )
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name="visitas",
        verbose_name="Venta asociada",
    )
    fecha = models.DateField(verbose_name="Fecha de visita")
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones",
    )

    class Meta:
        db_table = "visitas"
        verbose_name = "Visita"
        verbose_name_plural = "Visitas"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Visita #{self.pk} - Cliente {self.cliente_id}"

    def clean(self):
        if self.venta_id is None:
            return
        if self.cliente_id != self.venta.cliente_id:
            raise ValidationError(
                {"cliente": "El cliente de la visita debe coincidir con la venta."}
            )
        if self.empleado_id != self.venta.empleado_id:
            raise ValidationError(
                {"empleado": "El empleado de la visita debe coincidir con la venta."}
            )


class Comision(models.Model):
    empleado = models.ForeignKey(
        "empleados.Empleado",
        on_delete=models.PROTECT,
        related_name="comisiones",
        verbose_name="Empleado",
    )
    venta = models.ForeignKey(
        Venta,
        on_delete=models.PROTECT,
        related_name="comisiones",
        verbose_name="Venta",
    )
    venta_detalle_producto = models.ForeignKey(
        VentaDetalleProducto,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="comisiones",
        verbose_name="Detalle de producto",
    )
    venta_detalle_servicio = models.ForeignKey(
        VentaDetalleServicio,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="comisiones",
        verbose_name="Detalle de servicio",
    )
    porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=85.00,
        verbose_name="Porcentaje (%)",
    )
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Monto de la comision",
    )
    fecha = models.DateField(verbose_name="Fecha de comision")

    class Meta:
        db_table = "comisiones"
        verbose_name = "Comision"
        verbose_name_plural = "Comisiones"

    def clean(self):
        tiene_producto = self.venta_detalle_producto_id is not None
        tiene_servicio = self.venta_detalle_servicio_id is not None

        if not tiene_producto and not tiene_servicio:
            raise ValidationError(
                "Una comision debe estar asociada a un detalle de producto o a un detalle de servicio."
            )
        if tiene_producto and tiene_servicio:
            raise ValidationError(
                "Una comision no puede asociarse a producto y servicio al mismo tiempo."
            )
        if self.porcentaje <= 0 or self.porcentaje > 100:
            raise ValidationError({"porcentaje": "El porcentaje debe estar entre 0.01 y 100."})

    def save(self, *args, **kwargs):
        if self.venta_detalle_producto:
            base = self.venta_detalle_producto.subtotal
        elif self.venta_detalle_servicio:
            base = self.venta_detalle_servicio.subtotal
        else:
            base = Decimal("0")
        self.monto = (self.porcentaje / 100) * base
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comision #{self.pk} - Empleado {self.empleado_id}"
