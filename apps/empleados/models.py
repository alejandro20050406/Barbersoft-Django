import re

from django.core.exceptions import ValidationError
from django.db import models


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

    class Meta:
        db_table = "empleados"
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ["apellido", "nombre"]

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    def clean(self):
        if self.nombre:
            self.nombre = self.nombre.strip()
        if self.apellido:
            self.apellido = self.apellido.strip()
        if self.telefono:
            telefono_limpio = re.sub(r"\D", "", self.telefono.strip())
            if len(telefono_limpio) != 10:
                raise ValidationError(
                    {"telefono": "El numero de telefono debe tener exactamente 10 digitos."}
                )
            self.telefono = telefono_limpio
