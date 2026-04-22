from django.urls import path

from .views import (
    lista_empleados, EmpleadoListView, EmpleadoDetailView,
    EmpleadoCreateView, EmpleadoUpdateView, EmpleadoDeleteView
)

app_name = "empleados"

urlpatterns = [
    path("", lista_empleados, name="lista"),
    
    # Empleado URLs
    path("listado/", EmpleadoListView.as_view(), name="empleado-list"),
    path("<int:pk>/", EmpleadoDetailView.as_view(), name="empleado-detail"),
    path("crear/", EmpleadoCreateView.as_view(), name="empleado-create"),
    path("<int:pk>/editar/", EmpleadoUpdateView.as_view(), name="empleado-update"),
    path("<int:pk>/eliminar/", EmpleadoDeleteView.as_view(), name="empleado-delete"),
]
