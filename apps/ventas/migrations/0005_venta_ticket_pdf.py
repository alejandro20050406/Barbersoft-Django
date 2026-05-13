from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ventas", "0004_alter_comision_porcentaje"),
    ]

    operations = [
        migrations.AddField(
            model_name="venta",
            name="ticket_pdf",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="ventas/tickets/",
                verbose_name="Ticket PDF",
            ),
        ),
    ]
