from django.shortcuts import render
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from decimal import Decimal

from .models import Comision, Pago, Venta, Visita, VentaDetalleProducto, VentaDetalleServicio
from .forms import (
    ComisionForm, PagoForm, VentaForm, VisitaForm,
    VentaDetalleProductoForm, VentaDetalleServicioForm
)
from apps.catalogos.models import Producto, Servicio


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


# VENTA
class VentaListView(ListView):
    model = Venta
    template_name = 'ventas/venta_list.html'
    context_object_name = 'ventas'
    paginate_by = 20

    def get_queryset(self):
        queryset = Venta.objects.select_related('cliente', 'empleado', 'metodo_de_pago')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(cliente__nombre__icontains=search) |
                Q(cliente__apellido__icontains=search) |
                Q(empleado__nombre__icontains=search)
            )
        return queryset.order_by('-fecha')


class VentaDetailView(DetailView):
    model = Venta
    template_name = 'ventas/venta_detail.html'
    context_object_name = 'venta'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['detalles_productos'] = self.object.detalles_productos.select_related('producto')
        context['detalles_servicios'] = self.object.detalles_servicio.select_related('servicio')
        context['pagos'] = self.object.pagos.all()
        context['comisiones'] = self.object.comisiones.select_related('empleado')
        return context


class VentaCreateView(SuccessMessageMixin, CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'ventas/venta_form.html'
    success_url = reverse_lazy('ventas:venta-list')
    success_message = "Venta creada exitosamente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos'] = list(
            Producto.objects.filter(activo=True).values('id', 'nombre', 'precio_venta')
        )
        context['servicios'] = list(
            Servicio.objects.filter(activo=True).values('id', 'nombre', 'precio')
        )
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        item_types = self.request.POST.getlist('item_type')
        item_ids = self.request.POST.getlist('item_id')
        item_quantities = self.request.POST.getlist('item_quantity')

        tiene_items = any(
            item_type and item_id and item_quantity
            for item_type, item_id, item_quantity in zip(item_types, item_ids, item_quantities)
        )
        if not tiene_items:
            form.add_error(None, 'Agrega al menos un producto o servicio para esta venta.')
            return self.form_invalid(form)

        total = Decimal('0.00')
        self.object.total = total
        self.object.save()

        for item_type, item_id, item_quantity in zip(item_types, item_ids, item_quantities):
            if not item_type or not item_id or not item_quantity:
                continue
            try:
                quantity = int(item_quantity)
            except ValueError:
                continue
            if quantity <= 0:
                continue

            if item_type == 'producto':
                producto = Producto.objects.filter(id=item_id, activo=True).first()
                if not producto:
                    continue
                precio = producto.precio_venta
                subtotal = precio * quantity
                VentaDetalleProducto.objects.create(
                    venta=self.object,
                    producto=producto,
                    cantidad=quantity,
                    precio_unitario=precio,
                    subtotal=subtotal,
                )
            elif item_type == 'servicio':
                servicio = Servicio.objects.filter(id=item_id, activo=True).first()
                if not servicio:
                    continue
                precio = servicio.precio
                subtotal = precio * quantity
                VentaDetalleServicio.objects.create(
                    venta=self.object,
                    servicio=servicio,
                    precio_unitario=precio,
                    subtotal=subtotal,
                )
            else:
                continue

            total += subtotal

        self.object.total = total
        self.object.save(update_fields=['total'])
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return HttpResponseRedirect(self.get_success_url())


class VentaUpdateView(SuccessMessageMixin, UpdateView):
    model = Venta
    form_class = VentaForm
    template_name = 'ventas/venta_form.html'
    success_url = reverse_lazy('ventas:venta-list')
    success_message = "Venta actualizada exitosamente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos'] = list(
            Producto.objects.filter(activo=True).values('id', 'nombre', 'precio_venta')
        )
        context['servicios'] = list(
            Servicio.objects.filter(activo=True).values('id', 'nombre', 'precio')
        )
        return context


class VentaDeleteView(SuccessMessageMixin, DeleteView):
    model = Venta
    template_name = 'ventas/venta_confirm_delete.html'
    success_url = reverse_lazy('ventas:venta-list')
    success_message = "Venta eliminada exitosamente"


# PAGO
class PagoListView(ListView):
    model = Pago
    template_name = 'ventas/pago_list.html'
    context_object_name = 'pagos'
    paginate_by = 20

    def get_queryset(self):
        return Pago.objects.select_related('venta', 'metodo_de_pago').order_by('-fecha')


class PagoDetailView(DetailView):
    model = Pago
    template_name = 'ventas/pago_detail.html'
    context_object_name = 'pago'


class PagoCreateView(SuccessMessageMixin, CreateView):
    model = Pago
    form_class = PagoForm
    template_name = 'ventas/pago_form.html'
    success_url = reverse_lazy('ventas:pago-list')
    success_message = "Pago registrado exitosamente"


class PagoUpdateView(SuccessMessageMixin, UpdateView):
    model = Pago
    form_class = PagoForm
    template_name = 'ventas/pago_form.html'
    success_url = reverse_lazy('ventas:pago-list')
    success_message = "Pago actualizado exitosamente"


class PagoDeleteView(SuccessMessageMixin, DeleteView):
    model = Pago
    template_name = 'ventas/pago_confirm_delete.html'
    success_url = reverse_lazy('ventas:pago-list')
    success_message = "Pago eliminado exitosamente"


# VISITA
class VisitaListView(ListView):
    model = Visita
    template_name = 'ventas/visita_list.html'
    context_object_name = 'visitas'
    paginate_by = 20

    def get_queryset(self):
        return Visita.objects.select_related('cliente', 'empleado', 'venta').order_by('-fecha')


class VisitaDetailView(DetailView):
    model = Visita
    template_name = 'ventas/visita_detail.html'
    context_object_name = 'visita'


class VisitaCreateView(SuccessMessageMixin, CreateView):
    model = Visita
    form_class = VisitaForm
    template_name = 'ventas/visita_form.html'
    success_url = reverse_lazy('ventas:visita-list')
    success_message = "Visita registrada exitosamente"


class VisitaUpdateView(SuccessMessageMixin, UpdateView):
    model = Visita
    form_class = VisitaForm
    template_name = 'ventas/visita_form.html'
    success_url = reverse_lazy('ventas:visita-list')
    success_message = "Visita actualizada exitosamente"


class VisitaDeleteView(SuccessMessageMixin, DeleteView):
    model = Visita
    template_name = 'ventas/visita_confirm_delete.html'
    success_url = reverse_lazy('ventas:visita-list')
    success_message = "Visita eliminada exitosamente"


# COMISIÓN
class ComisionListView(ListView):
    model = Comision
    template_name = 'ventas/comision_list.html'
    context_object_name = 'comisiones'
    paginate_by = 20

    def get_queryset(self):
        return Comision.objects.select_related('empleado', 'venta').all()


class ComisionDetailView(DetailView):
    model = Comision
    template_name = 'ventas/comision_detail.html'
    context_object_name = 'comision'


class ComisionCreateView(SuccessMessageMixin, CreateView):
    model = Comision
    form_class = ComisionForm
    template_name = 'ventas/comision_form.html'
    success_url = reverse_lazy('ventas:comision-list')
    success_message = "Comisión registrada exitosamente"


class ComisionUpdateView(SuccessMessageMixin, UpdateView):
    model = Comision
    form_class = ComisionForm
    template_name = 'ventas/comision_form.html'
    success_url = reverse_lazy('ventas:comision-list')
    success_message = "Comisión actualizada exitosamente"


class ComisionDeleteView(SuccessMessageMixin, DeleteView):
    model = Comision
    template_name = 'ventas/comision_confirm_delete.html'
    success_url = reverse_lazy('ventas:comision-list')
    success_message = "Comisión eliminada exitosamente"


# VENTA DETALLE PRODUCTO
class VentaDetalleProductoListView(ListView):
    model = VentaDetalleProducto
    template_name = 'ventas/ventadetalleproducto_list.html'
    context_object_name = 'detalles_productos'
    paginate_by = 20

    def get_queryset(self):
        return VentaDetalleProducto.objects.select_related('venta', 'producto')


class VentaDetalleProductoDetailView(DetailView):
    model = VentaDetalleProducto
    template_name = 'ventas/ventadetalleproducto_detail.html'
    context_object_name = 'detalle_producto'


class VentaDetalleProductoCreateView(SuccessMessageMixin, CreateView):
    model = VentaDetalleProducto
    form_class = VentaDetalleProductoForm
    template_name = 'ventas/ventadetalleproducto_form.html'
    success_url = reverse_lazy('ventas:ventadetalleproducto-list')
    success_message = "Detalle de producto agregado exitosamente"


class VentaDetalleProductoUpdateView(SuccessMessageMixin, UpdateView):
    model = VentaDetalleProducto
    form_class = VentaDetalleProductoForm
    template_name = 'ventas/ventadetalleproducto_form.html'
    success_url = reverse_lazy('ventas:ventadetalleproducto-list')
    success_message = "Detalle de producto actualizado exitosamente"


class VentaDetalleProductoDeleteView(SuccessMessageMixin, DeleteView):
    model = VentaDetalleProducto
    template_name = 'ventas/ventadetalleproducto_confirm_delete.html'
    success_url = reverse_lazy('ventas:ventadetalleproducto-list')
    success_message = "Detalle de producto eliminado exitosamente"


# VENTA DETALLE SERVICIO
class VentaDetalleServicioListView(ListView):
    model = VentaDetalleServicio
    template_name = 'ventas/ventadetalleservicio_list.html'
    context_object_name = 'detalles_servicios'
    paginate_by = 20

    def get_queryset(self):
        return VentaDetalleServicio.objects.select_related('venta', 'servicio')


class VentaDetalleServicioDetailView(DetailView):
    model = VentaDetalleServicio
    template_name = 'ventas/ventadetalleservicio_detail.html'
    context_object_name = 'detalle_servicio'


class VentaDetalleServicioCreateView(SuccessMessageMixin, CreateView):
    model = VentaDetalleServicio
    form_class = VentaDetalleServicioForm
    template_name = 'ventas/ventadetalleservicio_form.html'
    success_url = reverse_lazy('ventas:ventadetalleservicio-list')
    success_message = "Detalle de servicio agregado exitosamente"


class VentaDetalleServicioUpdateView(SuccessMessageMixin, UpdateView):
    model = VentaDetalleServicio
    form_class = VentaDetalleServicioForm
    template_name = 'ventas/ventadetalleservicio_form.html'
    success_url = reverse_lazy('ventas:ventadetalleservicio-list')
    success_message = "Detalle de servicio actualizado exitosamente"


class VentaDetalleServicioDeleteView(SuccessMessageMixin, DeleteView):
    model = VentaDetalleServicio
    template_name = 'ventas/ventadetalleservicio_confirm_delete.html'
    success_url = reverse_lazy('ventas:ventadetalleservicio-list')
    success_message = "Detalle de servicio eliminado exitosamente"
