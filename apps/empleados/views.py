from django.shortcuts import render

from .models import Empleado


def lista_empleados(request):
    empleados = Empleado.objects.all()[:50]
    return render(request, "empleados/lista.html", {"empleados": empleados})
