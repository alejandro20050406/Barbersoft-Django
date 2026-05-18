from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ventas", "0006_alter_venta_fecha"),
    ]

    operations = [
        migrations.AlterField(
            model_name="venta",
            name="empleado",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="ventas",
                to="empleados.empleado",
                verbose_name="Empleado",
            ),
        ),
        migrations.AlterField(
            model_name="visita",
            name="empleado",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="visitas",
                to="empleados.empleado",
                verbose_name="Empleado",
            ),
        ),
    ]
