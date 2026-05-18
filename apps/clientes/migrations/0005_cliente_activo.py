from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clientes", "0004_alter_cliente_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="cliente",
            name="activo",
            field=models.BooleanField(default=True, verbose_name="Activo"),
        ),
    ]
