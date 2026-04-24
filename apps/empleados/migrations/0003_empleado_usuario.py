# Generated manually on 2026-04-24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def vincular_usuarios_existentes(apps, schema_editor):
    empleado_model = apps.get_model("empleados", "Empleado")
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    user_model = apps.get_model(app_label, model_name)
    admin_group_names = ("Administrador", "administrador")

    usuarios_usados = set()
    empleados = (
        empleado_model.objects.filter(usuario__isnull=True)
        .exclude(correo__isnull=True)
        .exclude(correo="")
    )
    for empleado in empleados:
        correo = empleado.correo.strip()
        if not correo:
            continue

        user = (
            user_model.objects.filter(email__iexact=correo)
            .filter(is_staff=False, is_superuser=False)
            .exclude(groups__name__in=admin_group_names)
            .exclude(id__in=usuarios_usados)
            .order_by("id")
            .first()
        )
        if user is None:
            user = (
                user_model.objects.filter(username__iexact=correo)
                .filter(is_staff=False, is_superuser=False)
                .exclude(groups__name__in=admin_group_names)
                .exclude(id__in=usuarios_usados)
                .order_by("id")
                .first()
            )
        if user is None:
            continue

        empleado.usuario_id = user.id
        empleado.save(update_fields=["usuario"])
        usuarios_usados.add(user.id)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("empleados", "0002_alter_empleado_apellido_alter_empleado_correo_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="empleado",
            name="usuario",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="empleado",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Usuario de acceso",
            ),
        ),
        migrations.RunPython(vincular_usuarios_existentes, migrations.RunPython.noop),
    ]
