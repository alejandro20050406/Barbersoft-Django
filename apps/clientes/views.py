from django.shortcuts import render

from .models import Cliente


def lista_clientes(request):
    clientes = Cliente.objects.all()[:50]
    return render(request, "clientes/lista.html", {"clientes": clientes})
