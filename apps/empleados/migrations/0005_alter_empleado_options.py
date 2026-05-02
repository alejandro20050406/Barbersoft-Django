from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("empleados", "0004_uppercase_empleado_names"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="empleado",
            options={
                "ordering": ["-fecha_registro", "-id"],
                "verbose_name": "Empleado",
                "verbose_name_plural": "Empleados",
            },
        ),
    ]
