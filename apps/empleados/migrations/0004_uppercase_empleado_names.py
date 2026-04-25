from django.db import migrations


def uppercase_empleado_names(apps, schema_editor):
    Empleado = apps.get_model("empleados", "Empleado")
    User = apps.get_model("auth", "User")

    for empleado in Empleado.objects.all().iterator():
        update_fields = []
        if empleado.nombre:
            empleado.nombre = empleado.nombre.strip().upper()
            update_fields.append("nombre")
        if empleado.apellido:
            empleado.apellido = empleado.apellido.strip().upper()
            update_fields.append("apellido")
        if update_fields:
            empleado.save(update_fields=update_fields)

        if empleado.usuario_id:
            user_updates = {}
            if empleado.nombre:
                user_updates["first_name"] = empleado.nombre
            if empleado.apellido:
                user_updates["last_name"] = empleado.apellido
            if user_updates:
                User.objects.filter(pk=empleado.usuario_id).update(**user_updates)


class Migration(migrations.Migration):

    dependencies = [
        ("empleados", "0003_empleado_usuario"),
    ]

    operations = [
        migrations.RunPython(uppercase_empleado_names, migrations.RunPython.noop),
    ]
