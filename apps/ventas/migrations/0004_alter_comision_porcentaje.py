from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ventas", "0003_alter_comision_options_alter_comision_fecha_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="comision",
            name="porcentaje",
            field=models.DecimalField(
                decimal_places=2,
                default=80.0,
                max_digits=5,
                verbose_name="Porcentaje (%)",
            ),
        ),
    ]
