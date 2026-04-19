from django.shortcuts import render

from .models import Comision, Pago, Venta, Visita


def dashboard_ventas(request):
    context = {
        "total_ventas": Venta.objects.count(),
        "total_pagos": Pago.objects.count(),
        "total_visitas": Visita.objects.count(),
        "total_comisiones": Comision.objects.count(),
        "ultimas_ventas": Venta.objects.select_related(
            "cliente", "empleado", "metodo_de_pago"
        ).all()[:10],
    }
    return render(request, "ventas/dashboard.html", context)
