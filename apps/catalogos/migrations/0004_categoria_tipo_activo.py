from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogos", "0003_uppercase_catalog_names"),
    ]

    operations = [
        migrations.AddField(
            model_name="categoriaproducto",
            name="activo",
            field=models.BooleanField(default=True, verbose_name="Activo"),
        ),
        migrations.AddField(
            model_name="tiposervicio",
            name="activo",
            field=models.BooleanField(default=True, verbose_name="Activo"),
        ),
    ]
