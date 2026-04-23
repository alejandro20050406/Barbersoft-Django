import re

from django.core.exceptions import ValidationError
from django.db import models


class Cliente(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    apellido = models.CharField(max_length=100, blank=True, null=True, verbose_name="Apellido")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefono")
    correo = models.EmailField(blank=True, null=True, verbose_name="Correo electronico")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")

    class Meta:
        db_table = "clientes"
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["apellido", "nombre"]

    def __str__(self):
        if self.apellido:
            return f"{self.nombre} {self.apellido}"
        return self.nombre

    def clean(self):
        if self.nombre:
            self.nombre = self.nombre.strip()
        if self.apellido:
            self.apellido = self.apellido.strip()
        if self.telefono:
            self.telefono = self.telefono.strip()
        if self.correo:
            self.correo = self.correo.strip().lower()

        if not self.nombre:
            raise ValidationError({"nombre": "El nombre es obligatorio."})

        if self.telefono and not re.match(r"^[\d\s\-\(\)\+]{7,20}$", self.telefono):
            raise ValidationError(
                {"telefono": "Ingresa un numero de telefono valido."}
            )
