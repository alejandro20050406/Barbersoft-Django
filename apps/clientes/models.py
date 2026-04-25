import re

from django.core.exceptions import ValidationError
from django.db import models


def _upper_clean(value):
    if value is None:
        return value
    return value.strip().upper()


class Cliente(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    apellido = models.CharField(max_length=100, blank=True, null=True, verbose_name="Apellido")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    correo = models.EmailField(blank=True, null=True, verbose_name="Correo electrónico")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")

    class Meta:
        db_table = "clientes"
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["apellido", "nombre"]

    def __str__(self):
        if self.apellido:
            return f"{self.nombre} {self.apellido}".upper()
        return self.nombre.upper()

    def clean(self):
        if self.nombre:
            self.nombre = _upper_clean(self.nombre)
        if self.apellido:
            self.apellido = _upper_clean(self.apellido)
        if not self.apellido:
            raise ValidationError({"apellido": "El apellido es obligatorio."})
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

        if not self.nombre:
            raise ValidationError({"nombre": "El nombre es obligatorio."})

    def save(self, *args, **kwargs):
        self.nombre = _upper_clean(self.nombre)
        if self.apellido:
            self.apellido = _upper_clean(self.apellido)
        if self.correo:
            self.correo = self.correo.strip().lower()
        super().save(*args, **kwargs)
