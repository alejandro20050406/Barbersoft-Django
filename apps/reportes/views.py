from django.db.models import Sum
from django.shortcuts import render

from apps.ventas.models import Pago, Venta


def dashboard_reportes(request):
    total_ventas = Venta.objects.count()
    total_pagos = Pago.objects.count()
    ingresos_venta = Venta.objects.aggregate(total=Sum("total"))["total"] or 0
    ingresos_pago = Pago.objects.aggregate(total=Sum("monto"))["total"] or 0

    context = {
        "total_ventas": total_ventas,
        "total_pagos": total_pagos,
        "ingresos_venta": ingresos_venta,
        "ingresos_pago": ingresos_pago,
    }
    return render(request, "reportes/dashboard.html", context)
