from django.db import migrations


def uppercase_nombre_fields(apps, schema_editor):
    model_names = [
        "CategoriaProducto",
        "Producto",
        "TipoServicio",
        "Servicio",
        "MetodoDePago",
    ]

    for model_name in model_names:
        model = apps.get_model("catalogos", model_name)
        for record in model.objects.all().iterator():
            if record.nombre:
                record.nombre = record.nombre.strip().upper()
                record.save(update_fields=["nombre"])


class Migration(migrations.Migration):

    dependencies = [
        ("catalogos", "0002_alter_categoriaproducto_descripcion_and_more"),
    ]

    operations = [
        migrations.RunPython(uppercase_nombre_fields, migrations.RunPython.noop),
    ]
