from django.urls import path

from .views import lista_empleados

app_name = "empleados"

urlpatterns = [
    path("", lista_empleados, name="lista"),
]
