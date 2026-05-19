from decimal import Decimal

from django.db import migrations, models
from django.db.models import Sum


def migrate_cancelled_sales(apps, schema_editor):
    Venta = apps.get_model("ventas", "Venta")
    VentaDetalleProducto = apps.get_model("ventas", "VentaDetalleProducto")
    VentaDetalleServicio = apps.get_model("ventas", "VentaDetalleServicio")

    for venta in Venta.objects.filter(total=Decimal("0.00")):
        productos_total = (
            VentaDetalleProducto.objects.filter(venta_id=venta.id).aggregate(
                total=Sum("subtotal")
            )["total"]
            or Decimal("0.00")
        )
        servicios_total = (
            VentaDetalleServicio.objects.filter(venta_id=venta.id).aggregate(
                total=Sum("subtotal")
            )["total"]
            or Decimal("0.00")
        )
        original_total = productos_total + servicios_total

        if original_total <= 0:
            continue

        venta.cancelada = True
        venta.total = original_total
        venta.save(update_fields=["cancelada", "total"])


class Migration(migrations.Migration):

    dependencies = [
        ("ventas", "0007_allow_admin_sales_without_employee"),
    ]

    operations = [
        migrations.AddField(
            model_name="venta",
            name="cancelada",
            field=models.BooleanField(default=False, verbose_name="Venta cancelada"),
        ),
        migrations.RunPython(migrate_cancelled_sales, migrations.RunPython.noop),
    ]
