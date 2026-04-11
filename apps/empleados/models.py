from django.db import models


class Empleado(models.Model):

    ACTIVO = "activo"
    INACTIVO = "inactivo"

    ESTADO_CHOICES = [
        (ACTIVO, "Activo"),
        (INACTIVO, "Inactivo"),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    porcentaje_comision = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Porcentaje de comisión general del empleado (ej. 10.00 = 10%)",
    )
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default=ACTIVO,
    )
    fecha_ingreso = models.DateField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "empleados"
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ["apellido", "nombre"]

    def __str__(self):
        return f"{self.nombre} {self.apellido}"