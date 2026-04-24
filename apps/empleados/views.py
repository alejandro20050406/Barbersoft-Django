from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import EmpleadoForm
from .models import Empleado


def lista_empleados(request):
    empleados = Empleado.objects.all()[:50]
    return render(request, "empleados/lista.html", {"empleados": empleados})


class EmpleadoListView(ListView):
    model = Empleado
    template_name = "empleados/empleado_list.html"
    context_object_name = "empleados"
    paginate_by = 20

    def get_queryset(self):
        queryset = Empleado.objects.all()
        search = self.request.GET.get("search")
        estado = self.request.GET.get("estado")
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search)
                | Q(apellido__icontains=search)
                | Q(telefono__icontains=search)
                | Q(correo__icontains=search)
            )
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["estados"] = Empleado.ESTADO_CHOICES
        return context


class EmpleadoDetailView(DetailView):
    model = Empleado
    template_name = "empleados/empleado_detail.html"
    context_object_name = "empleado"


class EmpleadoCreateView(SuccessMessageMixin, CreateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = "empleados/empleado_form.html"
    success_url = reverse_lazy("empleados:empleado-list")
    success_message = "Empleado creado exitosamente"


class EmpleadoUpdateView(SuccessMessageMixin, UpdateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = "empleados/empleado_form.html"
    success_url = reverse_lazy("empleados:empleado-list")
    success_message = "Empleado actualizado exitosamente"


class EmpleadoDeleteView(SuccessMessageMixin, DeleteView):
    model = Empleado
    template_name = "empleados/empleado_confirm_delete.html"
    success_url = reverse_lazy("empleados:empleado-list")
    success_message = "Empleado eliminado exitosamente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["back_url"] = self.success_url
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.estado == Empleado.INACTIVO:
            messages.info(request, "El empleado ya estaba inactivo.")
            return HttpResponseRedirect(self.success_url)

        self.object.estado = Empleado.INACTIVO
        self.object.save(update_fields=["estado"])

        if self.object.ventas.exists():
            messages.warning(
                request,
                "Empleado desactivado. Tiene ventas asociadas y no se elimino fisicamente.",
            )
        else:
            messages.success(request, "Empleado desactivado correctamente.")

        return HttpResponseRedirect(self.success_url)
