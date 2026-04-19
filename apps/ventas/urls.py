from django.urls import path

from .views import dashboard_ventas

app_name = "ventas"

urlpatterns = [
    path("", dashboard_ventas, name="dashboard"),
]
