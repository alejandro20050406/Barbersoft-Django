from django.core.exceptions import ValidationError
from django.db import models


def validar_precio_positivo(value):
    if value < 0:
        raise ValidationError("El precio no puede ser negativo.")


def validar_stock_positivo(value):
    if value < 0:
        raise ValidationError("El stock no puede ser negativo.")


class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        db_table = "categorias_de_productos"
        verbose_name = "Categoría de producto"
        verbose_name_plural = "Categorías de productos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def clean(self):
        if self.nombre:
            self.nombre = self.nombre.strip()


class Producto(models.Model):
    categoria = models.ForeignKey(
        CategoriaProducto,
        on_delete=models.PROTECT,
        related_name="productos",
        verbose_name="Categoría",
    )
    nombre = models.CharField(max_length=150, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    precio_compra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[validar_precio_positivo],
        verbose_name="Precio de compra",
    )
    precio_venta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[validar_precio_positivo],
        verbose_name="Precio de venta",
    )
    stock = models.PositiveIntegerField(
        default=0,
        validators=[validar_stock_positivo],
        verbose_name="Stock",
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")

    class Meta:
        db_table = "productos"
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} (${self.precio_venta})"

    def clean(self):
        if self.nombre:
            self.nombre = self.nombre.strip()
        if self.precio_compra is not None and self.precio_venta is not None:
            if self.precio_venta < self.precio_compra:
                raise ValidationError(
                    "El precio de venta no puede ser menor que el precio de compra."
                )


class TipoServicio(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        db_table = "tipos_de_servicios"
        verbose_name = "Tipo de servicio"
        verbose_name_plural = "Tipos de servicios"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def clean(self):
        if self.nombre:
            self.nombre = self.nombre.strip()


class Servicio(models.Model):
    tipo = models.ForeignKey(
        TipoServicio,
        on_delete=models.PROTECT,
        related_name="servicios",
        verbose_name="Tipo",
    )
    nombre = models.CharField(max_length=150, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[validar_precio_positivo],
        verbose_name="Precio",
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")

    class Meta:
        db_table = "servicios"
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} (${self.precio})"

    def clean(self):
        if self.nombre:
            self.nombre = self.nombre.strip()


# Nombre alineado con ventas: el Integrante 3 referencia 'catalogos.MetodoDePago'
class MetodoDePago(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        db_table = "metodos_de_pago"
        verbose_name = "Método de pago"
        verbose_name_plural = "Métodos de pago"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def clean(self):
        if self.nombre:
            self.nombre = self.nombre.strip()