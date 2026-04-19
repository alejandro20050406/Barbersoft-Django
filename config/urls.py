from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.accounts.urls")),
    path("catalogos/", include("apps.catalogos.urls")),
    path("clientes/", include("apps.clientes.urls")),
    path("empleados/", include("apps.empleados.urls")),
    path("ventas/", include("apps.ventas.urls")),
    path("reportes/", include("apps.reportes.urls")),
]
