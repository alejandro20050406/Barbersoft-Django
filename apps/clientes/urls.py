from django.urls import path

from .views import (
    lista_clientes, ClienteListView, ClienteDetailView,
    ClienteCreateView, ClienteUpdateView, ClienteDeleteView
)

app_name = "clientes"

urlpatterns = [
    path("", lista_clientes, name="lista"),
    
    # Cliente URLs
    path("listado/", ClienteListView.as_view(), name="cliente-list"),
    path("<int:pk>/", ClienteDetailView.as_view(), name="cliente-detail"),
    path("crear/", ClienteCreateView.as_view(), name="cliente-create"),
    path("<int:pk>/editar/", ClienteUpdateView.as_view(), name="cliente-update"),
    path("<int:pk>/eliminar/", ClienteDeleteView.as_view(), name="cliente-delete"),
]
