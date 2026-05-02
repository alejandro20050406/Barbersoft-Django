import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def _upper_clean(value):
    if value is None:
        return value
    return value.strip().upper()


def validar_porcentaje(value):
    if value < 0 or value > 100:
        raise ValidationError("El porcentaje de comisión debe estar entre 0 y 100.")


class Empleado(models.Model):

    ACTIVO = "activo"
    INACTIVO = "inactivo"

    ESTADO_CHOICES = [
        (ACTIVO, "Activo"),
        (INACTIVO, "Inactivo"),
    ]

    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    apellido = models.CharField(max_length=100, verbose_name="Apellido")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    correo = models.EmailField(blank=True, null=True, verbose_name="Correo electrónico")
    porcentaje_comision = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[validar_porcentaje],
        verbose_name="Porcentaje de comisión (%)",
        help_text="Valor entre 0.00 y 100.00",
    )
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default=ACTIVO,
        verbose_name="Estado",
    )
    fecha_ingreso = models.DateField(blank=True, null=True, verbose_name="Fecha de ingreso")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="empleado",
        verbose_name="Usuario de acceso",
    )

    class Meta:
        db_table = "empleados"
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ["-fecha_registro", "-id"]

    def __str__(self):
        return f"{self.nombre} {self.apellido}".upper()

    def clean(self):
        if self.nombre:
            self.nombre = _upper_clean(self.nombre)
        if self.apellido:
            self.apellido = _upper_clean(self.apellido)
        if self.nombre and not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+$", self.nombre):
            raise ValidationError({
                "nombre": "El nombre solo puede contener letras y espacios, sin signos especiales."
            })
        if self.apellido and not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+$", self.apellido):
            raise ValidationError({
                "apellido": "El apellido solo puede contener letras y espacios, sin signos especiales."
            })
        if not self.telefono:
            raise ValidationError({"telefono": "El teléfono es obligatorio."})

        telefono_limpio = re.sub(r"\D", "", self.telefono.strip())
        if len(telefono_limpio) != 10:
            raise ValidationError(
                {"telefono": "Número de teléfono inválido. Debe tener exactamente 10 dígitos."}
            )
        self.telefono = telefono_limpio

        if self.correo:
            self.correo = self.correo.strip().lower()

    def save(self, *args, **kwargs):
        self.nombre = _upper_clean(self.nombre)
        self.apellido = _upper_clean(self.apellido)
        if self.correo:
            self.correo = self.correo.strip().lower()
        super().save(*args, **kwargs)
