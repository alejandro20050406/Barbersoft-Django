from django.urls import path

from .views import dashboard_reportes

app_name = "reportes"

urlpatterns = [
    path("", dashboard_reportes, name="dashboard"),
]
