from datetime import timedelta
from decimal import Decimal

from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.utils import timezone

from apps.ventas.models import (
    Comision,
    Pago,
    Venta,
    VentaDetalleProducto,
    VentaDetalleServicio,
)


PERIODOS_CORTE = {
    "dia": "Dia",
    "semana": "Semana",
    "mes": "Mes",
    "anio": "Anual",
}


def _periodo_corte(periodo):
    periodo = periodo if periodo in PERIODOS_CORTE else "dia"
    today = timezone.localdate()

    if periodo == "semana":
        start_date = today - timedelta(days=today.weekday())
    elif periodo == "mes":
        start_date = today.replace(day=1)
    elif periodo == "anio":
        start_date = today.replace(month=1, day=1)
    else:
        start_date = today

    return periodo, PERIODOS_CORTE[periodo], start_date, today


def _money(value):
    return value or Decimal("0.00")


def dashboard_reportes(request):
    periodo, periodo_label, start_date, end_date = _periodo_corte(
        request.GET.get("periodo")
    )
    ventas_periodo = Venta.objects.filter(fecha__range=(start_date, end_date))
    pagos_periodo = Pago.objects.filter(fecha__range=(start_date, end_date))

    ingresos_venta = _money(
        ventas_periodo.aggregate(total=Coalesce(Sum("total"), Decimal("0.00")))["total"]
    )
    ingresos_pago = _money(
        pagos_periodo.aggregate(total=Coalesce(Sum("monto"), Decimal("0.00")))["total"]
    )
    ingresos_productos = _money(
        VentaDetalleProducto.objects.filter(venta__in=ventas_periodo).aggregate(
            total=Coalesce(Sum("subtotal"), Decimal("0.00"))
        )["total"]
    )
    ingresos_servicios = _money(
        VentaDetalleServicio.objects.filter(venta__in=ventas_periodo).aggregate(
            total=Coalesce(Sum("subtotal"), Decimal("0.00"))
        )["total"]
    )
    costo_productos = _money(
        VentaDetalleProducto.objects.filter(venta__in=ventas_periodo)
        .annotate(
            costo_linea=ExpressionWrapper(
                F("cantidad") * F("producto__precio_compra"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
        .aggregate(total=Coalesce(Sum("costo_linea"), Decimal("0.00")))["total"]
    )
    comisiones = _money(
        Comision.objects.filter(venta__in=ventas_periodo).aggregate(
            total=Coalesce(Sum("monto"), Decimal("0.00"))
        )["total"]
    )
    ganancia_neta = ingresos_venta - costo_productos - comisiones
    total_ventas = ventas_periodo.count()
    total_pagos = pagos_periodo.count()
    ticket_promedio = (
        ingresos_venta / total_ventas if total_ventas else Decimal("0.00")
    )

    desglose_pagos = (
        pagos_periodo.values("metodo_de_pago__nombre")
        .annotate(total=Coalesce(Sum("monto"), Decimal("0.00")))
        .order_by("-total", "metodo_de_pago__nombre")
    )

    context = {
        "periodos": PERIODOS_CORTE,
        "periodo": periodo,
        "periodo_label": periodo_label,
        "start_date": start_date,
        "end_date": end_date,
        "total_ventas": total_ventas,
        "total_pagos": total_pagos,
        "ingresos_venta": ingresos_venta,
        "ingresos_pago": ingresos_pago,
        "ingresos_productos": ingresos_productos,
        "ingresos_servicios": ingresos_servicios,
        "costo_productos": costo_productos,
        "comisiones": comisiones,
        "ganancia_neta": ganancia_neta,
        "ticket_promedio": ticket_promedio,
        "desglose_pagos": desglose_pagos,
        "ultimas_ventas": ventas_periodo.select_related(
            "cliente", "empleado", "metodo_de_pago"
        ).order_by("-fecha", "-id")[:8],
    }
    return render(request, "reportes/dashboard.html", context)
