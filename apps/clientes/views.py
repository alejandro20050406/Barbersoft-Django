import calendar

from django.shortcuts import render
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from django.utils import timezone

from .models import Cliente
from .forms import ClienteForm


FREQUENCY_FILTER_OPTIONS = {
    "3": "Ultimos 3 meses",
    "2": "Ultimos 2 meses",
    "1": "Ultimo mes",
}


def _months_ago(current_date, months):
    month = current_date.month - months
    year = current_date.year
    while month <= 0:
        month += 12
        year -= 1

    day = min(current_date.day, calendar.monthrange(year, month)[1])
    return current_date.replace(year=year, month=month, day=day)


def lista_clientes(request):
    clientes = Cliente.objects.filter(activo=True)[:50]
    return render(request, "clientes/lista.html", {"clientes": clientes})


# CLIENTE
class ClienteListView(ListView):
    model = Cliente
    template_name = 'clientes/cliente_list.html'
    context_object_name = 'clientes'
    paginate_by = 8

    def get_queryset(self):
        frequency_filter = self.request.GET.get("frecuencia")
        if frequency_filter in FREQUENCY_FILTER_OPTIONS:
            start_date = _months_ago(timezone.localdate(), int(frequency_filter))
            queryset = Cliente.objects.filter(activo=True).annotate(
                total_visitas=Count(
                    "visitas",
                    filter=Q(visitas__fecha__gte=start_date),
                )
            )
        else:
            queryset = Cliente.objects.filter(activo=True).annotate(
                total_visitas=Count("visitas")
            )
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(apellido__icontains=search) |
                Q(telefono__icontains=search) |
                Q(correo__icontains=search)
            )
        if frequency_filter in FREQUENCY_FILTER_OPTIONS:
            queryset = queryset.filter(total_visitas__gt=0).order_by(
                "-total_visitas", "apellido", "nombre"
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_frequency_filter = self.request.GET.get("frecuencia", "")
        context["frequency_filter_options"] = FREQUENCY_FILTER_OPTIONS
        context["selected_frequency_filter"] = (
            selected_frequency_filter
            if selected_frequency_filter in FREQUENCY_FILTER_OPTIONS
            else ""
        )
        return context


class ClienteDetailView(DetailView):
    model = Cliente
    template_name = 'clientes/cliente_detail.html'
    context_object_name = 'cliente'


class ClienteCreateView(SuccessMessageMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('clientes:cliente-list')
    success_message = "Cliente creado exitosamente"


class ClienteUpdateView(SuccessMessageMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('clientes:cliente-list')
    success_message = "Cliente actualizado exitosamente"


class ClienteDeleteView(SuccessMessageMixin, DeleteView):
    model = Cliente
    template_name = 'clientes/cliente_confirm_delete.html'
    success_url = reverse_lazy('clientes:cliente-list')
    success_message = "Cliente eliminado exitosamente"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["back_url"] = self.success_url
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            response = super().post(request, *args, **kwargs)
            messages.success(request, "Cliente eliminado correctamente.")
            return response
        except ProtectedError:
            self.object.activo = False
            self.object.save(update_fields=["activo"])
            messages.success(request, "Cliente eliminado del listado correctamente.")
            return HttpResponseRedirect(self.success_url)
