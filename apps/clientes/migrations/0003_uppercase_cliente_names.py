from django.db import migrations


def uppercase_cliente_names(apps, schema_editor):
    Cliente = apps.get_model("clientes", "Cliente")
    for cliente in Cliente.objects.all().iterator():
        update_fields = []
        if cliente.nombre:
            cliente.nombre = cliente.nombre.strip().upper()
            update_fields.append("nombre")
        if cliente.apellido:
            cliente.apellido = cliente.apellido.strip().upper()
            update_fields.append("apellido")
        if update_fields:
            cliente.save(update_fields=update_fields)


class Migration(migrations.Migration):

    dependencies = [
        ("clientes", "0002_alter_cliente_apellido_alter_cliente_correo_and_more"),
    ]

    operations = [
        migrations.RunPython(uppercase_cliente_names, migrations.RunPython.noop),
    ]
