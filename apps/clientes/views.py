from django.shortcuts import render
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q

from .models import Cliente
from .forms import ClienteForm


def lista_clientes(request):
    clientes = Cliente.objects.all()[:50]
    return render(request, "clientes/lista.html", {"clientes": clientes})


# CLIENTE
class ClienteListView(ListView):
    model = Cliente
    template_name = 'clientes/cliente_list.html'
    context_object_name = 'clientes'
    paginate_by = 20

    def get_queryset(self):
        queryset = Cliente.objects.all().annotate(total_visitas=Count("visitas"))
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(apellido__icontains=search) |
                Q(telefono__icontains=search) |
                Q(correo__icontains=search)
            )
        return queryset


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
        if self.object.ventas.exists():
            messages.error(
                request,
                "No se puede eliminar el cliente porque tiene ventas asociadas.",
            )
            return HttpResponseRedirect(self.success_url)
        return super().post(request, *args, **kwargs)
