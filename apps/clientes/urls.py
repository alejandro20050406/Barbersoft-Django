from django.urls import path

from .views import lista_clientes

app_name = "clientes"

urlpatterns = [
    path("", lista_clientes, name="lista"),
]
