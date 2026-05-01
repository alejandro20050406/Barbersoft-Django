from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import (
    CategoriaProductoForm,
    MetodoDePagoForm,
    ProductoForm,
    ServicioForm,
    TipoServicioForm,
)
from .models import CategoriaProducto, MetodoDePago, Producto, Servicio, TipoServicio


def dashboard(request):
    context = {
        "categorias": CategoriaProducto.objects.all()[:8],
        "metodos_pago": MetodoDePago.objects.all()[:8],
        "tipos_servicio": TipoServicio.objects.all()[:8],
        "productos": Producto.objects.select_related("categoria").filter(activo=True)[:8],
        "servicios": Servicio.objects.select_related("tipo").filter(activo=True)[:8],
    }
    return render(request, "catalogos/dashboard.html", context)


class DeleteContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["back_url"] = self.success_url
        return context


# CATEGORIA DE PRODUCTO
class CategoriaProductoListView(ListView):
    model = CategoriaProducto
    template_name = "catalogos/categoriaproducto_list.html"
    context_object_name = "categorias"
    paginate_by = 20

    def get_queryset(self):
        queryset = CategoriaProducto.objects.all()
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(nombre__icontains=search)
        return queryset


class CategoriaProductoDetailView(DetailView):
    model = CategoriaProducto
    template_name = "catalogos/categoriaproducto_detail.html"
    context_object_name = "categoria"


class CategoriaProductoCreateView(SuccessMessageMixin, CreateView):
    model = CategoriaProducto
    form_class = CategoriaProductoForm
    template_name = "catalogos/categoriaproducto_form.html"
    success_url = reverse_lazy("catalogos:categoria-list")
    success_message = "Categoria creada exitosamente"


class CategoriaProductoUpdateView(SuccessMessageMixin, UpdateView):
    model = CategoriaProducto
    form_class = CategoriaProductoForm
    template_name = "catalogos/categoriaproducto_form.html"
    success_url = reverse_lazy("catalogos:categoria-list")
    success_message = "Categoria actualizada exitosamente"


class CategoriaProductoDeleteView(DeleteContextMixin, SuccessMessageMixin, DeleteView):
    model = CategoriaProducto
    template_name = "catalogos/categoriaproducto_confirm_delete.html"
    success_url = reverse_lazy("catalogos:categoria-list")
    success_message = "Categoria eliminada exitosamente"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar la categoria porque tiene productos asociados.",
            )
            return HttpResponseRedirect(self.success_url)


# PRODUCTO
class ProductoListView(ListView):
    model = Producto
    template_name = "catalogos/producto_list.html"
    context_object_name = "productos"
    paginate_by = 20

    def get_queryset(self):
        queryset = Producto.objects.select_related("categoria")
        if self.request.GET.get("incluir_inactivos") != "1":
            queryset = queryset.filter(activo=True)

        search = self.request.GET.get("search")
        categoria = self.request.GET.get("categoria")
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | Q(descripcion__icontains=search)
            )
        if categoria:
            queryset = queryset.filter(categoria_id=categoria)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorias"] = CategoriaProducto.objects.all()
        return context


class ProductoDetailView(DetailView):
    model = Producto
    template_name = "catalogos/producto_detail.html"
    context_object_name = "producto"


class ProductoCreateView(SuccessMessageMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "catalogos/producto_form.html"
    success_url = reverse_lazy("catalogos:producto-list")
    success_message = "Producto creado exitosamente"


class ProductoUpdateView(SuccessMessageMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "catalogos/producto_form.html"
    success_url = reverse_lazy("catalogos:producto-list")
    success_message = "Producto actualizado exitosamente"


class ProductoDeleteView(DeleteContextMixin, SuccessMessageMixin, DeleteView):
    model = Producto
    template_name = "catalogos/producto_confirm_delete.html"
    success_url = reverse_lazy("catalogos:producto-list")
    success_message = "Producto eliminado exitosamente"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.activo:
            messages.info(request, "El producto ya estaba inactivo.")
            return HttpResponseRedirect(self.success_url)

        self.object.activo = False
        self.object.save(update_fields=["activo"])

        if self.object.detalles_venta.exists():
            messages.warning(
                request,
                "Producto desactivado. Tiene ventas asociadas y no se elimino fisicamente.",
            )
        else:
            messages.success(request, "Producto desactivado correctamente.")
        return HttpResponseRedirect(self.success_url)


# TIPO DE SERVICIO
class TipoServicioListView(ListView):
    model = TipoServicio
    template_name = "catalogos/tiposervicio_list.html"
    context_object_name = "tipos_servicio"
    paginate_by = 20

    def get_queryset(self):
        queryset = TipoServicio.objects.all()
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(nombre__icontains=search)
        return queryset


class TipoServicioDetailView(DetailView):
    model = TipoServicio
    template_name = "catalogos/tiposervicio_detail.html"
    context_object_name = "tipo_servicio"


class TipoServicioCreateView(SuccessMessageMixin, CreateView):
    model = TipoServicio
    form_class = TipoServicioForm
    template_name = "catalogos/tiposervicio_form.html"
    success_url = reverse_lazy("catalogos:tiposervicio-list")
    success_message = "Tipo de servicio creado exitosamente"


class TipoServicioUpdateView(SuccessMessageMixin, UpdateView):
    model = TipoServicio
    form_class = TipoServicioForm
    template_name = "catalogos/tiposervicio_form.html"
    success_url = reverse_lazy("catalogos:tiposervicio-list")
    success_message = "Tipo de servicio actualizado exitosamente"


class TipoServicioDeleteView(DeleteContextMixin, SuccessMessageMixin, DeleteView):
    model = TipoServicio
    template_name = "catalogos/tiposervicio_confirm_delete.html"
    success_url = reverse_lazy("catalogos:tiposervicio-list")
    success_message = "Tipo de servicio eliminado exitosamente"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar el tipo de servicio porque tiene servicios asociados.",
            )
            return HttpResponseRedirect(self.success_url)


# SERVICIO
class ServicioListView(ListView):
    model = Servicio
    template_name = "catalogos/servicio_list.html"
    context_object_name = "servicios"
    paginate_by = 20

    def get_queryset(self):
        queryset = Servicio.objects.select_related("tipo")
        if self.request.GET.get("incluir_inactivos") != "1":
            queryset = queryset.filter(activo=True)

        search = self.request.GET.get("search")
        tipo = self.request.GET.get("tipo")
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | Q(descripcion__icontains=search)
            )
        if tipo:
            queryset = queryset.filter(tipo_id=tipo)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tipos_servicio"] = TipoServicio.objects.all()
        return context


class ServicioDetailView(DetailView):
    model = Servicio
    template_name = "catalogos/servicio_detail.html"
    context_object_name = "servicio"


class ServicioCreateView(SuccessMessageMixin, CreateView):
    model = Servicio
    form_class = ServicioForm
    template_name = "catalogos/servicio_form.html"
    success_url = reverse_lazy("catalogos:servicio-list")
    success_message = "Servicio creado exitosamente"


class ServicioUpdateView(SuccessMessageMixin, UpdateView):
    model = Servicio
    form_class = ServicioForm
    template_name = "catalogos/servicio_form.html"
    success_url = reverse_lazy("catalogos:servicio-list")
    success_message = "Servicio actualizado exitosamente"


class ServicioDeleteView(DeleteContextMixin, SuccessMessageMixin, DeleteView):
    model = Servicio
    template_name = "catalogos/servicio_confirm_delete.html"
    success_url = reverse_lazy("catalogos:servicio-list")
    success_message = "Servicio eliminado exitosamente"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.activo:
            messages.info(request, "El servicio ya estaba inactivo.")
            return HttpResponseRedirect(self.success_url)

        self.object.activo = False
        self.object.save(update_fields=["activo"])

        if self.object.detalles_venta.exists():
            messages.warning(
                request,
                "Servicio desactivado. Tiene ventas asociadas y no se elimino fisicamente.",
            )
        else:
            messages.success(request, "Servicio desactivado correctamente.")
        return HttpResponseRedirect(self.success_url)


# METODO DE PAGO
class MetodoDePagoListView(ListView):
    model = MetodoDePago
    template_name = "catalogos/metododepago_list.html"
    context_object_name = "metodos_pago"
    paginate_by = 20

    def get_queryset(self):
        queryset = MetodoDePago.objects.all()
        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(nombre__icontains=search)
        return queryset


class MetodoDePagoDetailView(DetailView):
    model = MetodoDePago
    template_name = "catalogos/metododepago_detail.html"
    context_object_name = "metodo_pago"


class MetodoDePagoCreateView(SuccessMessageMixin, CreateView):
    model = MetodoDePago
    form_class = MetodoDePagoForm
    template_name = "catalogos/metododepago_form.html"
    success_url = reverse_lazy("catalogos:metodopago-list")
    success_message = "Metodo de pago creado exitosamente"


class MetodoDePagoUpdateView(SuccessMessageMixin, UpdateView):
    model = MetodoDePago
    form_class = MetodoDePagoForm
    template_name = "catalogos/metododepago_form.html"
    success_url = reverse_lazy("catalogos:metodopago-list")
    success_message = "Metodo de pago actualizado exitosamente"


class MetodoDePagoDeleteView(DeleteContextMixin, SuccessMessageMixin, DeleteView):
    model = MetodoDePago
    template_name = "catalogos/metododepago_confirm_delete.html"
    success_url = reverse_lazy("catalogos:metodopago-list")
    success_message = "Metodo de pago eliminado exitosamente"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar el metodo de pago porque tiene ventas o pagos asociados.",
            )
            return HttpResponseRedirect(self.success_url)
