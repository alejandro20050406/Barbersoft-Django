from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import redirect, render
from django.template.defaultfilters import slugify
from django.utils import timezone

from apps.catalogos.models import CategoriaProducto, MetodoDePago, Producto, Servicio
from apps.clientes.models import Cliente
from apps.empleados.models import Empleado
from apps.ventas.models import Venta

from .forms import LoginForm
from .roles import is_admin_user, is_employee_user


def menu_principal(request):
    if request.user.is_authenticated:
        return redirect(_menu_por_usuario(request.user))
    return render(request, "accounts/menu_principal.html")


def login_admin(request):
    return _login_por_rol(request, rol="admin")


def login_empleado(request):
    return _login_por_rol(request, rol="empleado")


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Sesion cerrada correctamente.")
    return redirect("accounts:menu-principal")


def menu_admin(request):
    if not request.user.is_authenticated:
        return redirect("accounts:menu-principal")
    if not is_admin_user(request.user):
        messages.error(request, "Solo administradores pueden entrar al menu admin.")
        return redirect(_menu_por_usuario(request.user))
    return render(request, "accounts/menu_admin.html", _build_admin_menu_context())


def menu_empleado(request):
    if not request.user.is_authenticated:
        return redirect("accounts:menu-principal")
    if is_admin_user(request.user):
        return redirect("accounts:menu-admin")
    if not is_employee_user(request.user):
        messages.error(request, "Tu usuario no tiene rol de empleado.")
        logout(request)
        return redirect("accounts:menu-principal")
    return render(
        request,
        "accounts/menu_empleado.html",
        _build_employee_menu_context(request.user),
    )


def home(request):
    if not request.user.is_authenticated:
        return redirect("accounts:menu-principal")
    if not is_admin_user(request.user):
        return redirect("accounts:menu-empleado")

    stats = {
        "categorias": CategoriaProducto.objects.count(),
        "metodos_pago": MetodoDePago.objects.count(),
        "productos": Producto.objects.count(),
        "servicios": Servicio.objects.count(),
        "clientes": Cliente.objects.count(),
        "empleados": Empleado.objects.count(),
        "ventas": Venta.objects.count(),
    }
    return render(request, "accounts/home.html", {"stats": stats})


def _login_por_rol(request, rol):
    if request.user.is_authenticated:
        return redirect(_menu_por_usuario(request.user))

    form = LoginForm(request.POST or None)
    es_admin = rol == "admin"
    titulo = "Inicio de sesion como Administrador" if es_admin else "Inicio de sesion como Empleado"

    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Usuario o contraseña incorrectos.")
        elif es_admin and not is_admin_user(user):
            messages.error(request, "Ese usuario no tiene permisos de administrador.")
        elif not es_admin and not is_employee_user(user):
            messages.error(request, "Ese usuario no tiene permisos de empleado.")
        else:
            login(request, user)
            return redirect("accounts:menu-admin" if es_admin else "accounts:menu-empleado")

    return render(
        request,
        "accounts/login.html",
        {
            "form": form,
            "titulo_login": titulo,
            "es_admin": es_admin,
        },
    )


def _menu_por_usuario(user):
    if is_admin_user(user):
        return "accounts:menu-admin"
    return "accounts:menu-empleado"


def _current_period():
    end_date = timezone.localdate()
    start_date = end_date - timedelta(days=29)
    return start_date, end_date


def _currency_amount(value):
    return value or Decimal("0.00")


def _employee_for_user(user):
    if not getattr(user, "is_authenticated", False):
        return None

    empleado = getattr(user, "empleado", None)
    if empleado is not None:
        return empleado

    filters = Q()
    if user.email:
        filters |= Q(correo__iexact=user.email)
    if user.username:
        filters |= Q(correo__iexact=user.username)
    if user.first_name and user.last_name:
        filters |= Q(nombre__iexact=user.first_name, apellido__iexact=user.last_name)

    if not filters:
        return None

    return Empleado.objects.filter(filters).order_by("id").first()


def _payment_breakdown(ventas_qs, pagos_qs=None, limit=4):
    source_qs = pagos_qs if pagos_qs is not None else ventas_qs
    total = (
        source_qs.aggregate(total=Coalesce(Sum("monto" if pagos_qs is not None else "total"), Decimal("0.00")))["total"]
        if pagos_qs is not None
        else source_qs.aggregate(total=Coalesce(Sum("total"), Decimal("0.00")))["total"]
    )

    if pagos_qs is not None:
        rows = (
            pagos_qs.values("metodo_de_pago__nombre")
            .annotate(total=Coalesce(Sum("monto"), Decimal("0.00")))
            .order_by("-total", "metodo_de_pago__nombre")[:limit]
        )
    else:
        rows = (
            ventas_qs.values("metodo_de_pago__nombre")
            .annotate(total=Coalesce(Sum("total"), Decimal("0.00")))
            .order_by("-total", "metodo_de_pago__nombre")[:limit]
        )

    breakdown = []
    for row in rows:
        amount = _currency_amount(row["total"])
        percentage = 0
        if total:
            percentage = round((amount / total) * 100, 1)
        breakdown.append(
            {
                "label": row["metodo_de_pago__nombre"],
                "amount": amount,
                "percentage": percentage,
            }
        )
    return breakdown


def _composition_summary(ventas_qs):
    servicios = ventas_qs.aggregate(
        total=Coalesce(Sum("detalles_servicio__subtotal"), Decimal("0.00"))
    )["total"]
    productos = ventas_qs.aggregate(
        total=Coalesce(Sum("detalles_productos__subtotal"), Decimal("0.00"))
    )["total"]
    total = _currency_amount(servicios) + _currency_amount(productos)

    def _part(label, amount):
        percentage = 0
        if total:
            percentage = round((amount / total) * 100, 1)
        return {"label": label, "amount": amount, "percentage": percentage}

    return {
        "servicios": _part("Servicios", _currency_amount(servicios)),
        "productos": _part("Productos", _currency_amount(productos)),
        "total": total,
    }


def _build_daily_series(ventas_qs, start_date, end_date):
    raw_rows = (
        ventas_qs.values("fecha")
        .annotate(total=Coalesce(Sum("total"), Decimal("0.00")))
        .order_by("fecha")
    )
    totals_by_date = {row["fecha"]: _currency_amount(row["total"]) for row in raw_rows}

    current = start_date
    series = []
    max_value = Decimal("0.00")
    while current <= end_date:
        amount = totals_by_date.get(current, Decimal("0.00"))
        if amount > max_value:
            max_value = amount
        series.append(
            {
                "date": current,
                "label": current.strftime("%d/%m"),
                "amount": amount,
            }
        )
        current += timedelta(days=1)

    if max_value <= 0:
        max_value = Decimal("1.00")

    for item in series:
        item["height"] = max(12, int((item["amount"] / max_value) * 100))

    return series


def _decorate_payment_breakdown(items):
    palette = ["green", "blue", "orange", "slate"]
    decorated = []
    for index, item in enumerate(items):
        tone = palette[index % len(palette)]
        decorated.append(
            {
                **item,
                "tone": tone,
                "tone_class": f"report-breakdown-fill-{tone}",
                "slug": slugify(item["label"]) or f"item-{index}",
            }
        )
    return decorated


def _build_admin_menu_context():
    start_date, end_date = _current_period()
    ventas_periodo = Venta.objects.filter(fecha__range=(start_date, end_date))

    costo_total = (
        ventas_periodo.filter(detalles_productos__isnull=False)
        .annotate(
            costo_item=ExpressionWrapper(
                F("detalles_productos__cantidad") * F("detalles_productos__producto__precio_compra"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
        .aggregate(total=Coalesce(Sum("costo_item"), Decimal("0.00")))["total"]
    )
    ingresos = ventas_periodo.aggregate(total=Coalesce(Sum("total"), Decimal("0.00")))["total"]
    ganancia = _currency_amount(ingresos) - _currency_amount(costo_total)

    ventas_recientes = (
        ventas_periodo.select_related("cliente", "empleado", "metodo_de_pago")
        .order_by("-fecha", "-id")[:6]
    )
    payment_breakdown = _decorate_payment_breakdown(_payment_breakdown(ventas_periodo))

    top_servicios = (
        ventas_periodo.filter(detalles_servicio__isnull=False)
        .values("detalles_servicio__servicio__nombre")
        .annotate(total=Count("detalles_servicio"), ingresos=Coalesce(Sum("detalles_servicio__subtotal"), Decimal("0.00")))
        .order_by("-total", "-ingresos", "detalles_servicio__servicio__nombre")[:3]
    )
    top_productos = (
        ventas_periodo.filter(detalles_productos__isnull=False)
        .values("detalles_productos__producto__nombre")
        .annotate(
            total=Coalesce(Sum("detalles_productos__cantidad"), 0),
            ingresos=Coalesce(Sum("detalles_productos__subtotal"), Decimal("0.00")),
        )
        .order_by("-total", "-ingresos", "detalles_productos__producto__nombre")[:3]
    )
    top_empleados = (
        ventas_periodo.values("empleado__nombre", "empleado__apellido")
        .annotate(total_ventas=Count("id"), ingresos=Coalesce(Sum("total"), Decimal("0.00")))
        .order_by("-ingresos", "-total_ventas", "empleado__apellido")[:3]
    )

    return {
        "dashboard": {
            "role_label": "Administrador",
            "period_label": "Ultimos 30 dias",
            "start_date": start_date,
            "end_date": end_date,
            "stats": [
                {"title": "Ingresos Totales", "value": _currency_amount(ingresos), "accent": "blue", "is_currency": True},
                {"title": "Costos", "value": _currency_amount(costo_total), "accent": "orange", "is_currency": True},
                {"title": "Ganancia Neta", "value": ganancia, "accent": "green", "is_currency": True},
                {"title": "Ventas Registradas", "value": ventas_periodo.count(), "accent": "slate", "is_currency": False},
            ],
            "highlights": [
                {"label": "Clientes registrados", "value": Cliente.objects.count()},
                {"label": "Empleados activos", "value": Empleado.objects.filter(estado=Empleado.ACTIVO).count()},
                {"label": "Productos activos", "value": Producto.objects.filter(activo=True).count()},
                {"label": "Servicios activos", "value": Servicio.objects.filter(activo=True).count()},
            ],
            "daily_series": _build_daily_series(ventas_periodo, start_date, end_date),
            "composition": _composition_summary(ventas_periodo),
            "payment_breakdown": payment_breakdown,
            "recent_sales": ventas_recientes,
            "top_services": list(top_servicios),
            "top_products": list(top_productos),
            "top_employees": list(top_empleados),
        }
    }


def _build_employee_menu_context(user):
    empleado = _employee_for_user(user)
    start_date, end_date = _current_period()

    ventas_periodo = Venta.objects.none()
    if empleado is not None:
        ventas_periodo = Venta.objects.filter(
            empleado=empleado,
            fecha__range=(start_date, end_date),
        )

    ingresos = ventas_periodo.aggregate(total=Coalesce(Sum("total"), Decimal("0.00")))["total"]
    comisiones = (
        empleado.comisiones.filter(fecha__range=(start_date, end_date)).aggregate(
            total=Coalesce(Sum("monto"), Decimal("0.00"))
        )["total"]
        if empleado is not None
        else Decimal("0.00")
    )
    clientes_atendidos = ventas_periodo.values("cliente_id").distinct().count()
    visitas_registradas = ventas_periodo.values("visitas__id").distinct().count()

    ventas_recientes = (
        ventas_periodo.select_related("cliente", "metodo_de_pago")
        .order_by("-fecha", "-id")[:6]
    )
    payment_breakdown = _decorate_payment_breakdown(_payment_breakdown(ventas_periodo))
    top_servicios = (
        ventas_periodo.filter(detalles_servicio__isnull=False)
        .values("detalles_servicio__servicio__nombre")
        .annotate(total=Count("detalles_servicio"), ingresos=Coalesce(Sum("detalles_servicio__subtotal"), Decimal("0.00")))
        .order_by("-total", "-ingresos", "detalles_servicio__servicio__nombre")[:3]
    )
    top_productos = (
        ventas_periodo.filter(detalles_productos__isnull=False)
        .values("detalles_productos__producto__nombre")
        .annotate(
            total=Coalesce(Sum("detalles_productos__cantidad"), 0),
            ingresos=Coalesce(Sum("detalles_productos__subtotal"), Decimal("0.00")),
        )
        .order_by("-total", "-ingresos", "detalles_productos__producto__nombre")[:3]
    )

    return {
        "dashboard": {
            "role_label": "Empleado",
            "employee_name": str(empleado) if empleado is not None else user.get_username(),
            "period_label": "Ultimos 30 dias",
            "start_date": start_date,
            "end_date": end_date,
            "stats": [
                {"title": "Mis Ingresos", "value": _currency_amount(ingresos), "accent": "blue", "is_currency": True},
                {"title": "Mis Comisiones", "value": _currency_amount(comisiones), "accent": "green", "is_currency": True},
                {"title": "Ventas Realizadas", "value": ventas_periodo.count(), "accent": "slate", "is_currency": False},
                {"title": "Clientes Atendidos", "value": clientes_atendidos, "accent": "orange", "is_currency": False},
            ],
            "highlights": [
                {"label": "Visitas registradas", "value": visitas_registradas},
                {"label": "Metodo principal", "value": payment_breakdown[0]["label"] if payment_breakdown else "-"},
                {"label": "Promedio por venta", "value": (_currency_amount(ingresos) / ventas_periodo.count()) if ventas_periodo.count() else Decimal("0.00")},
            ],
            "daily_series": _build_daily_series(ventas_periodo, start_date, end_date),
            "composition": _composition_summary(ventas_periodo),
            "payment_breakdown": payment_breakdown,
            "recent_sales": ventas_recientes,
            "top_services": list(top_servicios),
            "top_products": list(top_productos),
            "empleado": empleado,
        }
    }
