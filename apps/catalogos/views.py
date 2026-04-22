from django.shortcuts import render
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q

from .models import CategoriaProducto, MetodoDePago, Producto, Servicio, TipoServicio
from .forms import (
    CategoriaProductoForm, MetodoDePagoForm, ProductoForm, 
    ServicioForm, TipoServicioForm
)


def dashboard(request):
    context = {
        "categorias": CategoriaProducto.objects.all()[:8],
        "metodos_pago": MetodoDePago.objects.all()[:8],
        "tipos_servicio": TipoServicio.objects.all()[:8],
        "productos_recientes": Producto.objects.select_related("categoria").all()[:8],
        "servicios_recientes": Servicio.objects.select_related("tipo").all()[:8],
    }
    return render(request, "catalogos/dashboard.html", context)


# CATEGORÍA DE PRODUCTO
class CategoriaProductoListView(ListView):
    model = CategoriaProducto
    template_name = 'catalogos/categoriaproducto_list.html'
    context_object_name = 'categorias'
    paginate_by = 20

    def get_queryset(self):
        queryset = CategoriaProducto.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(nombre__icontains=search)
        return queryset


class CategoriaProductoDetailView(DetailView):
    model = CategoriaProducto
    template_name = 'catalogos/categoriaproducto_detail.html'
    context_object_name = 'categoria'


class CategoriaProductoCreateView(SuccessMessageMixin, CreateView):
    model = CategoriaProducto
    form_class = CategoriaProductoForm
    template_name = 'catalogos/categoriaproducto_form.html'
    success_url = reverse_lazy('catalogos:categoria-list')
    success_message = "Categoría creada exitosamente"


class CategoriaProductoUpdateView(SuccessMessageMixin, UpdateView):
    model = CategoriaProducto
    form_class = CategoriaProductoForm
    template_name = 'catalogos/categoriaproducto_form.html'
    success_url = reverse_lazy('catalogos:categoria-list')
    success_message = "Categoría actualizada exitosamente"


class CategoriaProductoDeleteView(SuccessMessageMixin, DeleteView):
    model = CategoriaProducto
    template_name = 'catalogos/categoriaproducto_confirm_delete.html'
    success_url = reverse_lazy('catalogos:categoria-list')
    success_message = "Categoría eliminada exitosamente"


# PRODUCTO
class ProductoListView(ListView):
    model = Producto
    template_name = 'catalogos/producto_list.html'
    context_object_name = 'productos'
    paginate_by = 20

    def get_queryset(self):
        queryset = Producto.objects.select_related('categoria')
        search = self.request.GET.get('search')
        categoria = self.request.GET.get('categoria')
        if search:
            queryset = queryset.filter(Q(nombre__icontains=search) | Q(descripcion__icontains=search))
        if categoria:
            queryset = queryset.filter(categoria_id=categoria)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = CategoriaProducto.objects.all()
        return context


class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'catalogos/producto_detail.html'
    context_object_name = 'producto'


class ProductoCreateView(SuccessMessageMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'catalogos/producto_form.html'
    success_url = reverse_lazy('catalogos:producto-list')
    success_message = "Producto creado exitosamente"


class ProductoUpdateView(SuccessMessageMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'catalogos/producto_form.html'
    success_url = reverse_lazy('catalogos:producto-list')
    success_message = "Producto actualizado exitosamente"


class ProductoDeleteView(SuccessMessageMixin, DeleteView):
    model = Producto
    template_name = 'catalogos/producto_confirm_delete.html'
    success_url = reverse_lazy('catalogos:producto-list')
    success_message = "Producto eliminado exitosamente"


# TIPO DE SERVICIO
class TipoServicioListView(ListView):
    model = TipoServicio
    template_name = 'catalogos/tiposervicio_list.html'
    context_object_name = 'tipos_servicio'
    paginate_by = 20

    def get_queryset(self):
        queryset = TipoServicio.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(nombre__icontains=search)
        return queryset


class TipoServicioDetailView(DetailView):
    model = TipoServicio
    template_name = 'catalogos/tiposervicio_detail.html'
    context_object_name = 'tipo_servicio'


class TipoServicioCreateView(SuccessMessageMixin, CreateView):
    model = TipoServicio
    form_class = TipoServicioForm
    template_name = 'catalogos/tiposervicio_form.html'
    success_url = reverse_lazy('catalogos:tiposervicio-list')
    success_message = "Tipo de servicio creado exitosamente"


class TipoServicioUpdateView(SuccessMessageMixin, UpdateView):
    model = TipoServicio
    form_class = TipoServicioForm
    template_name = 'catalogos/tiposervicio_form.html'
    success_url = reverse_lazy('catalogos:tiposervicio-list')
    success_message = "Tipo de servicio actualizado exitosamente"


class TipoServicioDeleteView(SuccessMessageMixin, DeleteView):
    model = TipoServicio
    template_name = 'catalogos/tiposervicio_confirm_delete.html'
    success_url = reverse_lazy('catalogos:tiposervicio-list')
    success_message = "Tipo de servicio eliminado exitosamente"


# SERVICIO
class ServicioListView(ListView):
    model = Servicio
    template_name = 'catalogos/servicio_list.html'
    context_object_name = 'servicios'
    paginate_by = 20

    def get_queryset(self):
        queryset = Servicio.objects.select_related('tipo')
        search = self.request.GET.get('search')
        tipo = self.request.GET.get('tipo')
        if search:
            queryset = queryset.filter(Q(nombre__icontains=search) | Q(descripcion__icontains=search))
        if tipo:
            queryset = queryset.filter(tipo_id=tipo)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos_servicio'] = TipoServicio.objects.all()
        return context


class ServicioDetailView(DetailView):
    model = Servicio
    template_name = 'catalogos/servicio_detail.html'
    context_object_name = 'servicio'


class ServicioCreateView(SuccessMessageMixin, CreateView):
    model = Servicio
    form_class = ServicioForm
    template_name = 'catalogos/servicio_form.html'
    success_url = reverse_lazy('catalogos:servicio-list')
    success_message = "Servicio creado exitosamente"


class ServicioUpdateView(SuccessMessageMixin, UpdateView):
    model = Servicio
    form_class = ServicioForm
    template_name = 'catalogos/servicio_form.html'
    success_url = reverse_lazy('catalogos:servicio-list')
    success_message = "Servicio actualizado exitosamente"


class ServicioDeleteView(SuccessMessageMixin, DeleteView):
    model = Servicio
    template_name = 'catalogos/servicio_confirm_delete.html'
    success_url = reverse_lazy('catalogos:servicio-list')
    success_message = "Servicio eliminado exitosamente"


# MÉTODO DE PAGO
class MetodoDePagoListView(ListView):
    model = MetodoDePago
    template_name = 'catalogos/metododepago_list.html'
    context_object_name = 'metodos_pago'
    paginate_by = 20

    def get_queryset(self):
        queryset = MetodoDePago.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(nombre__icontains=search)
        return queryset


class MetodoDePagoDetailView(DetailView):
    model = MetodoDePago
    template_name = 'catalogos/metododepago_detail.html'
    context_object_name = 'metodo_pago'


class MetodoDePagoCreateView(SuccessMessageMixin, CreateView):
    model = MetodoDePago
    form_class = MetodoDePagoForm
    template_name = 'catalogos/metododepago_form.html'
    success_url = reverse_lazy('catalogos:metodopago-list')
    success_message = "Método de pago creado exitosamente"


class MetodoDePagoUpdateView(SuccessMessageMixin, UpdateView):
    model = MetodoDePago
    form_class = MetodoDePagoForm
    template_name = 'catalogos/metododepago_form.html'
    success_url = reverse_lazy('catalogos:metodopago-list')
    success_message = "Método de pago actualizado exitosamente"


class MetodoDePagoDeleteView(SuccessMessageMixin, DeleteView):
    model = MetodoDePago
    template_name = 'catalogos/metododepago_confirm_delete.html'
    success_url = reverse_lazy('catalogos:metodopago-list')
    success_message = "Método de pago eliminado exitosamente"
