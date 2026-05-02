from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, Sum
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.accounts.roles import is_admin_user, is_employee_user
from apps.catalogos.models import CategoriaProducto, Producto, Servicio, TipoServicio
from apps.clientes.models import Cliente
from apps.empleados.models import Empleado

from .forms import (
    ComisionForm,
    PagoForm,
    VentaDetalleProductoForm,
    VentaDetalleServicioForm,
    VentaForm,
    VisitaForm,
)
from .models import Comision, Pago, Venta, VentaDetalleProducto, VentaDetalleServicio, Visita

EMPLOYEE_SERVICE_PERCENTAGE = Decimal("80.00")
ADMIN_SERVICE_PERCENTAGE = Decimal("20.00")


def _parse_iso_date(raw_value):
    if not raw_value:
        return None
    try:
        return date.fromisoformat(raw_value)
    except ValueError:
        return None


def _validation_error_text(exc):
    if hasattr(exc, "message_dict"):
        parts = []
        for field, errors in exc.message_dict.items():
            for err in errors:
                parts.append(f"{field}: {err}")
        return " | ".join(parts)
    if hasattr(exc, "messages"):
        return " ".join(exc.messages)
    return str(exc)


def _cliente_option_text(cliente):
    if isinstance(cliente, dict):
        nombre = cliente.get("nombre", "")
        apellido = cliente.get("apellido")
        telefono = cliente.get("telefono")
    else:
        nombre = cliente.nombre
        apellido = cliente.apellido
        telefono = cliente.telefono

    full_name = nombre
    if apellido:
        full_name = f"{full_name} {apellido}"
    if telefono:
        full_name = f"{full_name} ({telefono})"
    return full_name.upper()


def _selected_cliente_from_form(form):
    raw_cliente_id = ""
    if form.is_bound:
        raw_cliente_id = form.data.get(form.add_prefix("cliente"), "")
    elif form.instance and form.instance.pk:
        raw_cliente_id = form.instance.cliente_id
    elif form.initial.get("cliente"):
        raw_cliente_id = form.initial["cliente"]

    if not raw_cliente_id:
        return None

    cliente = Cliente.objects.filter(pk=raw_cliente_id).first()
    if cliente is None:
        return None

    return {"id": cliente.id, "text": _cliente_option_text(cliente)}


def _employee_ids_for_user(user, only_active=False):
    if not getattr(user, "is_authenticated", False):
        return []

    if is_admin_user(user):
        queryset = Empleado.objects.all()
        if only_active:
            queryset = queryset.filter(estado=Empleado.ACTIVO)
        return list(queryset.values_list("id", flat=True))

    empleado_vinculado = getattr(user, "empleado", None)
    if empleado_vinculado:
        if only_active and empleado_vinculado.estado != Empleado.ACTIVO:
            return []
        return [empleado_vinculado.id]

    filters = Q()
    email = (getattr(user, "email", "") or "").strip()
    username = (getattr(user, "username", "") or "").strip()
    first_name = (getattr(user, "first_name", "") or "").strip()
    last_name = (getattr(user, "last_name", "") or "").strip()

    if email:
        filters |= Q(correo__iexact=email)
    if username:
        filters |= Q(correo__iexact=username)
    if first_name and last_name:
        filters |= Q(nombre__iexact=first_name, apellido__iexact=last_name)

    if not filters:
        return []

    queryset = Empleado.objects.filter(filters).distinct()
    if only_active:
        queryset = queryset.filter(estado=Empleado.ACTIVO)
    return list(queryset.values_list("id", flat=True))


def _scope_ventas_queryset(request, queryset):
    if is_admin_user(request.user):
        return queryset
    if is_employee_user(request.user):
        employee_ids = _employee_ids_for_user(request.user)
        if employee_ids:
            return queryset.filter(empleado_id__in=employee_ids)
        return queryset.none()
    return queryset.none()


def _request_has_item_payload(request):
    payload = []
    payload.extend(request.POST.getlist("item_type"))
    payload.extend(request.POST.getlist("item_id"))
    payload.extend(request.POST.getlist("item_quantity"))
    return any((value or "").strip() for value in payload)


def _parse_item_rows(request):
    item_types = request.POST.getlist("item_type")
    item_ids = request.POST.getlist("item_id")
    item_quantities = request.POST.getlist("item_quantity")

    max_len = max(len(item_types), len(item_ids), len(item_quantities))
    if max_len == 0:
        raise ValidationError("Agrega al menos un producto o servicio para la venta.")

    rows = []
    for index in range(max_len):
        item_type = item_types[index].strip() if index < len(item_types) else ""
        item_id = item_ids[index].strip() if index < len(item_ids) else ""
        item_quantity = (
            item_quantities[index].strip() if index < len(item_quantities) else ""
        )

        if not item_type and not item_id and not item_quantity:
            continue

        if not item_type or not item_id or not item_quantity:
            raise ValidationError(
                f"Fila {index + 1}: completa tipo, item y cantidad."
            )

        if item_type not in {"producto", "servicio"}:
            raise ValidationError(f"Fila {index + 1}: el tipo de item no es valido.")

        try:
            parsed_id = int(item_id)
        except ValueError as exc:
            raise ValidationError(f"Fila {index + 1}: el item seleccionado no es valido.") from exc

        try:
            quantity = int(item_quantity)
        except ValueError as exc:
            raise ValidationError(f"Fila {index + 1}: la cantidad debe ser un entero.") from exc

        if quantity <= 0:
            raise ValidationError(f"Fila {index + 1}: la cantidad debe ser mayor a cero.")

        rows.append(
            {
                "item_type": item_type,
                "item_id": parsed_id,
                "quantity": quantity,
            }
        )

    if not rows:
        raise ValidationError("Agrega al menos un item valido para la venta.")

    return rows


def _resolve_sale_lines(rows):
    lines = []
    total = Decimal("0.00")

    for index, row in enumerate(rows, start=1):
        quantity = row["quantity"]

        if row["item_type"] == "producto":
            producto = (
                Producto.objects.select_for_update()
                .filter(pk=row["item_id"], activo=True)
                .first()
            )
            if producto is None:
                raise ValidationError(
                    f"Fila {index}: el producto no existe o esta inactivo."
                )
            if producto.stock < quantity:
                raise ValidationError(
                    f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}."
                )

            precio = producto.precio_venta
            subtotal = precio * quantity
            lines.append(
                {
                    "kind": "producto",
                    "record": producto,
                    "quantity": quantity,
                    "precio": precio,
                    "subtotal": subtotal,
                }
            )
        else:
            servicio = Servicio.objects.filter(pk=row["item_id"], activo=True).first()
            if servicio is None:
                raise ValidationError(
                    f"Fila {index}: el servicio no existe o esta inactivo."
                )
            precio = servicio.precio
            subtotal = precio * quantity
            lines.append(
                {
                    "kind": "servicio",
                    "record": servicio,
                    "quantity": quantity,
                    "precio": precio,
                    "subtotal": subtotal,
                }
            )

        total += subtotal

    if total <= 0:
        raise ValidationError("El total de la venta debe ser mayor a cero.")

    return lines, total


def _restore_stock_for_sale(venta):
    detalles = (
        venta.detalles_productos.select_related("producto")
        .select_for_update()
        .all()
    )
    for detalle in detalles:
        producto = detalle.producto
        producto.stock += detalle.cantidad
        producto.save(update_fields=["stock"])


def _apply_lines_to_sale(venta, lines):
    for line in lines:
        if line["kind"] == "producto":
            producto = line["record"]
            producto.stock -= line["quantity"]
            if producto.stock < 0:
                raise ValidationError(
                    f"Stock insuficiente para {producto.nombre} al confirmar la venta."
                )
            producto.save(update_fields=["stock"])

            VentaDetalleProducto.objects.create(
                venta=venta,
                producto=producto,
                cantidad=line["quantity"],
                precio_unitario=line["precio"],
                subtotal=line["subtotal"],
            )
        else:
            detalle_servicio = VentaDetalleServicio.objects.create(
                venta=venta,
                servicio=line["record"],
                precio_unitario=line["precio"],
                subtotal=line["subtotal"],
            )
            _create_service_commission(venta, detalle_servicio)


def _create_service_commission(venta, detalle_servicio):
    Comision.objects.create(
        empleado=venta.empleado,
        venta=venta,
        venta_detalle_servicio=detalle_servicio,
        porcentaje=EMPLOYEE_SERVICE_PERCENTAGE,
        fecha=venta.fecha,
    )


def _ensure_visit_for_sale(venta):
    visita = Visita.objects.filter(venta=venta).order_by("id").first()
    if visita is None:
        Visita.objects.create(
            cliente=venta.cliente,
            empleado=venta.empleado,
            venta=venta,
            fecha=venta.fecha,
        )
        return

    update_fields = []
    if visita.cliente_id != venta.cliente_id:
        visita.cliente = venta.cliente
        update_fields.append("cliente")
    if visita.empleado_id != venta.empleado_id:
        visita.empleado = venta.empleado
        update_fields.append("empleado")
    if visita.fecha != venta.fecha:
        visita.fecha = venta.fecha
        update_fields.append("fecha")

    if update_fields:
        visita.save(update_fields=update_fields)


def _recalculate_sale_total(venta):
    total_productos = (
        venta.detalles_productos.aggregate(total=Sum("subtotal")).get("total")
        or Decimal("0.00")
    )
    total_servicios = (
        venta.detalles_servicio.aggregate(total=Sum("subtotal")).get("total")
        or Decimal("0.00")
    )
    return total_productos + total_servicios


def _service_profit_summary(venta):
    service_total = (
        venta.detalles_servicio.aggregate(total=Sum("subtotal")).get("total")
        or Decimal("0.00")
    )
    empleado_total = (service_total * EMPLOYEE_SERVICE_PERCENTAGE) / Decimal("100")
    admin_total = (service_total * ADMIN_SERVICE_PERCENTAGE) / Decimal("100")
    return {
        "service_total": service_total,
        "empleado_total": empleado_total,
        "admin_total": admin_total,
        "empleado_percentage": EMPLOYEE_SERVICE_PERCENTAGE,
        "admin_percentage": ADMIN_SERVICE_PERCENTAGE,
    }


def _sale_is_cancelled(venta):
    if venta.total != Decimal("0.00"):
        return False
    return venta.detalles_productos.exists() or venta.detalles_servicio.exists()


def dashboard_ventas(request):
    ventas_qs = _scope_ventas_queryset(
        request,
        Venta.objects.select_related("cliente", "empleado", "metodo_de_pago"),
    )

    context = {
        "total_ventas": ventas_qs.count(),
        "total_pagos": Pago.objects.filter(venta__in=ventas_qs).count(),
        "total_visitas": Visita.objects.filter(venta__in=ventas_qs).count(),
        "total_comisiones": Comision.objects.filter(venta__in=ventas_qs).count(),
        "ultimas_ventas": ventas_qs.order_by("-fecha")[:10],
    }
    return render(request, "ventas/dashboard.html", context)


class VentaListView(ListView):
    model = Venta
    template_name = "ventas/venta_list.html"
    context_object_name = "ventas"
    paginate_by = 8

    def get_queryset(self):
        queryset = Venta.objects.select_related("cliente", "empleado", "metodo_de_pago")
        queryset = _scope_ventas_queryset(self.request, queryset)

        search = self.request.GET.get("search")
        fecha_desde_raw = self.request.GET.get("fecha_desde")
        fecha_hasta_raw = self.request.GET.get("fecha_hasta")

        if search:
            queryset = queryset.filter(
                Q(cliente__nombre__icontains=search)
                | Q(cliente__apellido__icontains=search)
                | Q(empleado__nombre__icontains=search)
                | Q(empleado__apellido__icontains=search)
            )

        fecha_desde = _parse_iso_date(fecha_desde_raw)
        if fecha_desde_raw and fecha_desde is None:
            messages.error(self.request, "Fecha desde invalida. Usa formato YYYY-MM-DD.")
        if fecha_desde:
            queryset = queryset.filter(fecha__gte=fecha_desde)

        fecha_hasta = _parse_iso_date(fecha_hasta_raw)
        if fecha_hasta_raw and fecha_hasta is None:
            messages.error(self.request, "Fecha hasta invalida. Usa formato YYYY-MM-DD.")
        if fecha_hasta:
            queryset = queryset.filter(fecha__lte=fecha_hasta)

        return queryset.order_by("-fecha")


class VentaDetailView(DetailView):
    model = Venta
    template_name = "ventas/venta_detail.html"
    context_object_name = "venta"

    def get_queryset(self):
        queryset = Venta.objects.select_related("cliente", "empleado", "metodo_de_pago")
        return _scope_ventas_queryset(self.request, queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["detalles_productos"] = self.object.detalles_productos.select_related(
            "producto"
        )
        context["detalles_servicios"] = self.object.detalles_servicio.select_related(
            "servicio"
        )
        context["pagos"] = self.object.pagos.all()
        context["comisiones"] = self.object.comisiones.select_related("empleado")
        context["service_profit_summary"] = _service_profit_summary(self.object)
        return context


class VentaCreateView(SuccessMessageMixin, CreateView):
    model = Venta
    form_class = VentaForm
    template_name = "ventas/venta_form.html"
    success_url = reverse_lazy("ventas:venta-list")
    success_message = "Venta creada exitosamente"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request_user"] = self.request.user
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if is_employee_user(self.request.user) and not is_admin_user(self.request.user):
            employee_ids = _employee_ids_for_user(self.request.user, only_active=True)
            form.fields["empleado"].queryset = form.fields["empleado"].queryset.filter(
                pk__in=employee_ids
            )
            # Pre-set the employee to current user's employee for new sales
            if not self.kwargs.get('pk'):  # Only for create, not update
                employee = None
                if employee_ids:
                    employee = Empleado.objects.filter(pk__in=employee_ids).first()
                else:
                    # Fallback: try to find employee by email or username
                    user = self.request.user
                    if user.email:
                        employee = Empleado.objects.filter(
                            Q(correo__iexact=user.email) | Q(correo__iexact=user.username),
                            estado=Empleado.ACTIVO
                        ).first()
                    if not employee and user.first_name and user.last_name:
                        employee = Empleado.objects.filter(
                            nombre__iexact=user.first_name,
                            apellido__iexact=user.last_name,
                            estado=Empleado.ACTIVO
                        ).first()
                
                if employee:
                    form.initial["empleado"] = employee
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_cliente"] = _selected_cliente_from_form(context["form"])
        initial_item_type = (self.request.GET.get("item_type") or "").strip().lower()
        if initial_item_type not in {"producto", "servicio"}:
            initial_item_type = ""

        context["initial_item_type"] = initial_item_type
        context["categorias_producto"] = list(
            CategoriaProducto.objects.values("id", "nombre")
        )
        context["tipos_servicio"] = list(TipoServicio.objects.values("id", "nombre"))
        context["productos"] = list(
            Producto.objects.filter(activo=True, stock__gt=0).values(
                "id", "nombre", "precio_venta", "categoria_id"
            )
        )
        context["servicios"] = list(
            Servicio.objects.filter(activo=True).values("id", "nombre", "precio", "tipo_id")
        )
        
        # Check if user is an employee (not admin)
        context["is_employee"] = is_employee_user(self.request.user) and not is_admin_user(self.request.user)
        if context["is_employee"]:
            employee_ids = _employee_ids_for_user(self.request.user, only_active=True)
            if employee_ids:
                employee = Empleado.objects.filter(pk__in=employee_ids).first()
                context["current_employee"] = employee
            else:
                # Fallback: try to find employee by email or username
                user = self.request.user
                employee = None
                if user.email:
                    employee = Empleado.objects.filter(
                        Q(correo__iexact=user.email) | Q(correo__iexact=user.username),
                        estado=Empleado.ACTIVO
                    ).first()
                if not employee and user.first_name and user.last_name:
                    employee = Empleado.objects.filter(
                        nombre__iexact=user.first_name,
                        apellido__iexact=user.last_name,
                        estado=Empleado.ACTIVO
                    ).first()
                context["current_employee"] = employee
        
        return context

    def form_valid(self, form):
        try:
            rows = _parse_item_rows(self.request)
        except ValidationError as exc:
            form.add_error(None, _validation_error_text(exc))
            return self.form_invalid(form)

        empleado = form.cleaned_data.get("empleado")
        if is_employee_user(self.request.user) and not is_admin_user(self.request.user):
            employee_ids = _employee_ids_for_user(self.request.user, only_active=True)
            if not employee_ids:
                form.add_error(
                    None,
                    "Tu usuario no esta vinculado a un empleado activo. Contacta al administrador.",
                )
                return self.form_invalid(form)
            if empleado is None or empleado.id not in employee_ids:
                form.add_error(
                    "empleado",
                    "Solo puedes registrar ventas para tu propio perfil de empleado.",
                )
                return self.form_invalid(form)

        try:
            with transaction.atomic():
                venta = form.save(commit=False)
                venta.total = Decimal("0.00")
                venta.save()

                lines, total = _resolve_sale_lines(rows)
                _apply_lines_to_sale(venta, lines)

                venta.total = total
                venta.save(update_fields=["total"])
                _ensure_visit_for_sale(venta)
                self.object = venta
        except ValidationError as exc:
            form.add_error(None, _validation_error_text(exc))
            return self.form_invalid(form)

        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.get_success_url())


class VentaUpdateView(SuccessMessageMixin, UpdateView):
    model = Venta
    form_class = VentaForm
    template_name = "ventas/venta_form.html"
    success_url = reverse_lazy("ventas:venta-list")
    success_message = "Venta actualizada exitosamente"

    def get_queryset(self):
        queryset = Venta.objects.select_related("cliente", "empleado", "metodo_de_pago")
        return _scope_ventas_queryset(self.request, queryset)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request_user"] = self.request.user
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if is_employee_user(self.request.user) and not is_admin_user(self.request.user):
            employee_ids = _employee_ids_for_user(self.request.user, only_active=True)
            form.fields["empleado"].queryset = form.fields["empleado"].queryset.filter(
                pk__in=employee_ids
            )
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["productos"] = list(
            Producto.objects.filter(activo=True).values("id", "nombre", "precio_venta")
        )
        context["servicios"] = list(
            Servicio.objects.filter(activo=True).values("id", "nombre", "precio")
        )
        return context

    def form_valid(self, form):
        venta_actual = self.get_object()

        if _sale_is_cancelled(venta_actual):
            form.add_error(None, "No puedes editar una venta cancelada.")
            return self.form_invalid(form)

        empleado = form.cleaned_data.get("empleado")
        if is_employee_user(self.request.user) and not is_admin_user(self.request.user):
            employee_ids = _employee_ids_for_user(self.request.user, only_active=True)
            if not employee_ids:
                form.add_error(
                    None,
                    "Tu usuario no esta vinculado a un empleado activo. Contacta al administrador.",
                )
                return self.form_invalid(form)
            if empleado is None or empleado.id not in employee_ids:
                form.add_error(
                    "empleado",
                    "Solo puedes registrar ventas para tu propio perfil de empleado.",
                )
                return self.form_invalid(form)

        try:
            with transaction.atomic():
                venta = form.save(commit=False)
                has_item_payload = _request_has_item_payload(self.request)
                tiene_historico = venta_actual.pagos.exists() or venta_actual.comisiones.exists()
                cambia_encabezado = any(
                    [
                        venta.cliente_id != venta_actual.cliente_id,
                        venta.empleado_id != venta_actual.empleado_id,
                        venta.metodo_de_pago_id != venta_actual.metodo_de_pago_id,
                        venta.fecha != venta_actual.fecha,
                    ]
                )

                if tiene_historico and cambia_encabezado:
                    raise ValidationError(
                        "No puedes modificar cliente, empleado, fecha o metodo de pago en una venta con historial."
                    )

                if has_item_payload:
                    if tiene_historico:
                        raise ValidationError(
                            "No puedes modificar items en una venta con pagos o comisiones registradas."
                        )

                    rows = _parse_item_rows(self.request)

                    _restore_stock_for_sale(venta_actual)
                    venta_actual.detalles_productos.all().delete()
                    venta_actual.detalles_servicio.all().delete()

                    lines, total = _resolve_sale_lines(rows)
                    _apply_lines_to_sale(venta_actual, lines)
                    venta.total = total
                else:
                    venta.total = _recalculate_sale_total(venta_actual)

                if venta.total <= 0:
                    raise ValidationError(
                        "La venta debe conservar un total mayor a cero para ser valida."
                    )

                venta.save()
                _ensure_visit_for_sale(venta)
                self.object = venta
        except ValidationError as exc:
            form.add_error(None, _validation_error_text(exc))
            return self.form_invalid(form)

        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.get_success_url())


class VentaDeleteView(SuccessMessageMixin, DeleteView):
    model = Venta
    template_name = "ventas/venta_confirm_delete.html"
    success_url = reverse_lazy("ventas:venta-list")
    success_message = "Venta eliminada exitosamente"

    def get_queryset(self):
        queryset = Venta.objects.select_related("cliente", "empleado", "metodo_de_pago")
        return _scope_ventas_queryset(self.request, queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["back_url"] = self.success_url
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if _sale_is_cancelled(self.object):
            messages.info(request, "La venta ya estaba cancelada.")
            return HttpResponseRedirect(self.success_url)

        try:
            with transaction.atomic():
                _restore_stock_for_sale(self.object)
                self.object.total = Decimal("0.00")
                self.object.save(update_fields=["total"])
        except ValidationError as exc:
            messages.error(request, _validation_error_text(exc))
            return HttpResponseRedirect(self.success_url)

        messages.success(
            request,
            "Venta cancelada correctamente. Se conservo el historico y se repuso inventario de productos.",
        )
        return HttpResponseRedirect(self.success_url)


class PagoListView(ListView):
    model = Pago
    template_name = "ventas/pago_list.html"
    context_object_name = "pagos"
    paginate_by = 20

    def get_queryset(self):
        queryset = Pago.objects.select_related("venta", "metodo_de_pago")
        if is_admin_user(self.request.user):
            return queryset.order_by("-fecha")
        employee_ids = _employee_ids_for_user(self.request.user)
        if not employee_ids:
            return queryset.none()
        return queryset.filter(venta__empleado_id__in=employee_ids).order_by("-fecha")


class PagoDetailView(DetailView):
    model = Pago
    template_name = "ventas/pago_detail.html"
    context_object_name = "pago"

    def get_queryset(self):
        queryset = Pago.objects.select_related("venta", "metodo_de_pago")
        if is_admin_user(self.request.user):
            return queryset
        employee_ids = _employee_ids_for_user(self.request.user)
        if not employee_ids:
            return queryset.none()
        return queryset.filter(venta__empleado_id__in=employee_ids)


class PagoCreateView(SuccessMessageMixin, CreateView):
    model = Pago
    form_class = PagoForm
    template_name = "ventas/pago_form.html"
    success_url = reverse_lazy("ventas:pago-list")
    success_message = "Pago registrado exitosamente"


class PagoUpdateView(SuccessMessageMixin, UpdateView):
    model = Pago
    form_class = PagoForm
    template_name = "ventas/pago_form.html"
    success_url = reverse_lazy("ventas:pago-list")
    success_message = "Pago actualizado exitosamente"


class PagoDeleteView(SuccessMessageMixin, DeleteView):
    model = Pago
    template_name = "ventas/pago_confirm_delete.html"
    success_url = reverse_lazy("ventas:pago-list")
    success_message = "Pago eliminado exitosamente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["back_url"] = self.success_url
        return context


class VisitaListView(ListView):
    model = Visita
    template_name = "ventas/visita_list.html"
    context_object_name = "visitas"
    paginate_by = 20

    def get_queryset(self):
        queryset = Visita.objects.select_related("cliente", "empleado", "venta")
        if is_admin_user(self.request.user):
            return queryset.order_by("-fecha")
        employee_ids = _employee_ids_for_user(self.request.user)
        if not employee_ids:
            return queryset.none()
        return queryset.filter(empleado_id__in=employee_ids).order_by("-fecha")


class VisitaDetailView(DetailView):
    model = Visita
    template_name = "ventas/visita_detail.html"
    context_object_name = "visita"


class VisitaCreateView(SuccessMessageMixin, CreateView):
    model = Visita
    form_class = VisitaForm
    template_name = "ventas/visita_form.html"
    success_url = reverse_lazy("ventas:visita-list")
    success_message = "Visita registrada exitosamente"


class VisitaUpdateView(SuccessMessageMixin, UpdateView):
    model = Visita
    form_class = VisitaForm
    template_name = "ventas/visita_form.html"
    success_url = reverse_lazy("ventas:visita-list")
    success_message = "Visita actualizada exitosamente"


class VisitaDeleteView(SuccessMessageMixin, DeleteView):
    model = Visita
    template_name = "ventas/visita_confirm_delete.html"
    success_url = reverse_lazy("ventas:visita-list")
    success_message = "Visita eliminada exitosamente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["back_url"] = self.success_url
        return context


class ComisionListView(ListView):
    model = Comision
    template_name = "ventas/comision_list.html"
    context_object_name = "comisiones"
    paginate_by = 20

    def get_queryset(self):
        queryset = Comision.objects.select_related("empleado", "venta")
        if is_admin_user(self.request.user):
            return queryset
        employee_ids = _employee_ids_for_user(self.request.user)
        if not employee_ids:
            return queryset.none()
        return queryset.filter(empleado_id__in=employee_ids)


class ComisionDetailView(DetailView):
    model = Comision
    template_name = "ventas/comision_detail.html"
    context_object_name = "comision"


class ComisionCreateView(SuccessMessageMixin, CreateView):
    model = Comision
    form_class = ComisionForm
    template_name = "ventas/comision_form.html"
    success_url = reverse_lazy("ventas:comision-list")
    success_message = "Comision registrada exitosamente"


class ComisionUpdateView(SuccessMessageMixin, UpdateView):
    model = Comision
    form_class = ComisionForm
    template_name = "ventas/comision_form.html"
    success_url = reverse_lazy("ventas:comision-list")
    success_message = "Comision actualizada exitosamente"


class ComisionDeleteView(SuccessMessageMixin, DeleteView):
    model = Comision
    template_name = "ventas/comision_confirm_delete.html"
    success_url = reverse_lazy("ventas:comision-list")
    success_message = "Comision eliminada exitosamente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["back_url"] = self.success_url
        return context


class VentaDetalleProductoListView(ListView):
    model = VentaDetalleProducto
    template_name = "ventas/ventadetalleproducto_list.html"
    context_object_name = "detalles_productos"
    paginate_by = 20

    def get_queryset(self):
        return VentaDetalleProducto.objects.select_related("venta", "producto")


class VentaDetalleProductoDetailView(DetailView):
    model = VentaDetalleProducto
    template_name = "ventas/ventadetalleproducto_detail.html"
    context_object_name = "detalle_producto"


class VentaDetalleProductoCreateView(SuccessMessageMixin, CreateView):
    model = VentaDetalleProducto
    form_class = VentaDetalleProductoForm
    template_name = "ventas/ventadetalleproducto_form.html"
    success_url = reverse_lazy("ventas:ventadetalleproducto-list")
    success_message = "Detalle de producto agregado exitosamente"


class VentaDetalleProductoUpdateView(SuccessMessageMixin, UpdateView):
    model = VentaDetalleProducto
    form_class = VentaDetalleProductoForm
    template_name = "ventas/ventadetalleproducto_form.html"
    success_url = reverse_lazy("ventas:ventadetalleproducto-list")
    success_message = "Detalle de producto actualizado exitosamente"


class VentaDetalleProductoDeleteView(SuccessMessageMixin, DeleteView):
    model = VentaDetalleProducto
    template_name = "ventas/ventadetalleproducto_confirm_delete.html"
    success_url = reverse_lazy("ventas:ventadetalleproducto-list")
    success_message = "Detalle de producto eliminado exitosamente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["back_url"] = self.success_url
        return context


class VentaDetalleServicioListView(ListView):
    model = VentaDetalleServicio
    template_name = "ventas/ventadetalleservicio_list.html"
    context_object_name = "detalles_servicios"
    paginate_by = 20

    def get_queryset(self):
        return VentaDetalleServicio.objects.select_related("venta", "servicio")


class VentaDetalleServicioDetailView(DetailView):
    model = VentaDetalleServicio
    template_name = "ventas/ventadetalleservicio_detail.html"
    context_object_name = "detalle_servicio"


class VentaDetalleServicioCreateView(SuccessMessageMixin, CreateView):
    model = VentaDetalleServicio
    form_class = VentaDetalleServicioForm
    template_name = "ventas/ventadetalleservicio_form.html"
    success_url = reverse_lazy("ventas:ventadetalleservicio-list")
    success_message = "Detalle de servicio agregado exitosamente"


class VentaDetalleServicioUpdateView(SuccessMessageMixin, UpdateView):
    model = VentaDetalleServicio
    form_class = VentaDetalleServicioForm
    template_name = "ventas/ventadetalleservicio_form.html"
    success_url = reverse_lazy("ventas:ventadetalleservicio-list")
    success_message = "Detalle de servicio actualizado exitosamente"


class VentaDetalleServicioDeleteView(SuccessMessageMixin, DeleteView):
    model = VentaDetalleServicio
    template_name = "ventas/ventadetalleservicio_confirm_delete.html"
    success_url = reverse_lazy("ventas:ventadetalleservicio-list")
    success_message = "Detalle de servicio eliminado exitosamente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["back_url"] = self.success_url
        return context


def api_clientes_search(request):
    """API endpoint que devuelve clientes filtrados por búsqueda."""
    query = request.GET.get('q', '').strip()
    if not query or len(query) < 2:
        return JsonResponse({'results': []})

    filters = Q()
    for token in query.split():
        filters &= (
            Q(nombre__icontains=token)
            | Q(apellido__icontains=token)
            | Q(telefono__icontains=token)
            | Q(correo__icontains=token)
        )

    clientes = (
        Cliente.objects.filter(filters)
        .order_by('apellido', 'nombre')
        .values('id', 'nombre', 'apellido', 'telefono')[:20]
    )
    
    results = []
    for cliente in clientes:
        results.append({
            'id': cliente['id'],
            'text': _cliente_option_text(cliente)
        })
    
    return JsonResponse({'results': results})
