from django.shortcuts import render

from apps.catalogos.models import CategoriaProducto, MetodoDePago, Producto, Servicio
from apps.clientes.models import Cliente
from apps.empleados.models import Empleado
from apps.ventas.models import Venta


def home(request):
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
