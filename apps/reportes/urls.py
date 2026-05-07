from django.urls import path

from .views import dashboard_reportes, exportar_reporte_pdf

app_name = "reportes"

urlpatterns = [
    path("", dashboard_reportes, name="dashboard"),
    path("pdf/", exportar_reporte_pdf, name="dashboard-pdf"),
]
