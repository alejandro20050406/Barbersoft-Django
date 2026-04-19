from django.shortcuts import render

from .models import CategoriaProducto, MetodoDePago, Producto, Servicio, TipoServicio


def dashboard(request):
    context = {
        "categorias": CategoriaProducto.objects.all()[:8],
        "metodos_pago": MetodoDePago.objects.all()[:8],
        "tipos_servicio": TipoServicio.objects.all()[:8],
        "productos_recientes": Producto.objects.select_related("categoria").all()[:8],
        "servicios_recientes": Servicio.objects.select_related("tipo").all()[:8],
    }
    return render(request, "catalogos/dashboard.html", context)
