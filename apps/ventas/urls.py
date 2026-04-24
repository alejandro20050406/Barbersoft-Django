from django.urls import path

from .views import (
    dashboard_ventas,
    api_clientes_search,
    # Venta
    VentaListView, VentaDetailView, VentaCreateView, VentaUpdateView, VentaDeleteView,
    # Pago
    PagoListView, PagoDetailView, PagoCreateView, PagoUpdateView, PagoDeleteView,
    # Visita
    VisitaListView, VisitaDetailView, VisitaCreateView, VisitaUpdateView, VisitaDeleteView,
    # Comisión
    ComisionListView, ComisionDetailView, ComisionCreateView, ComisionUpdateView, ComisionDeleteView,
    # Venta Detalle Producto
    VentaDetalleProductoListView, VentaDetalleProductoDetailView,
    VentaDetalleProductoCreateView, VentaDetalleProductoUpdateView, VentaDetalleProductoDeleteView,
    # Venta Detalle Servicio
    VentaDetalleServicioListView, VentaDetalleServicioDetailView,
    VentaDetalleServicioCreateView, VentaDetalleServicioUpdateView, VentaDetalleServicioDeleteView,
)

app_name = "ventas"

urlpatterns = [
    path("", dashboard_ventas, name="dashboard"),
    path("api/clientes-search/", api_clientes_search, name="api-clientes-search"),
    
    # Venta URLs
    path("ventas/", VentaListView.as_view(), name="venta-list"),
    path("ventas/<int:pk>/", VentaDetailView.as_view(), name="venta-detail"),
    path("ventas/crear/", VentaCreateView.as_view(), name="venta-create"),
    path("ventas/<int:pk>/editar/", VentaUpdateView.as_view(), name="venta-update"),
    path("ventas/<int:pk>/eliminar/", VentaDeleteView.as_view(), name="venta-delete"),
    
    # Pago URLs
    path("pagos/", PagoListView.as_view(), name="pago-list"),
    path("pagos/<int:pk>/", PagoDetailView.as_view(), name="pago-detail"),
    path("pagos/crear/", PagoCreateView.as_view(), name="pago-create"),
    path("pagos/<int:pk>/editar/", PagoUpdateView.as_view(), name="pago-update"),
    path("pagos/<int:pk>/eliminar/", PagoDeleteView.as_view(), name="pago-delete"),
    
    # Visita URLs
    path("visitas/", VisitaListView.as_view(), name="visita-list"),
    path("visitas/<int:pk>/", VisitaDetailView.as_view(), name="visita-detail"),
    path("visitas/crear/", VisitaCreateView.as_view(), name="visita-create"),
    path("visitas/<int:pk>/editar/", VisitaUpdateView.as_view(), name="visita-update"),
    path("visitas/<int:pk>/eliminar/", VisitaDeleteView.as_view(), name="visita-delete"),
    
    # Comisión URLs
    path("comisiones/", ComisionListView.as_view(), name="comision-list"),
    path("comisiones/<int:pk>/", ComisionDetailView.as_view(), name="comision-detail"),
    path("comisiones/crear/", ComisionCreateView.as_view(), name="comision-create"),
    path("comisiones/<int:pk>/editar/", ComisionUpdateView.as_view(), name="comision-update"),
    path("comisiones/<int:pk>/eliminar/", ComisionDeleteView.as_view(), name="comision-delete"),
    
    # Venta Detalle Producto URLs
    path("detalles-productos/", VentaDetalleProductoListView.as_view(), name="ventadetalleproducto-list"),
    path("detalles-productos/<int:pk>/", VentaDetalleProductoDetailView.as_view(), name="ventadetalleproducto-detail"),
    path("detalles-productos/crear/", VentaDetalleProductoCreateView.as_view(), name="ventadetalleproducto-create"),
    path("detalles-productos/<int:pk>/editar/", VentaDetalleProductoUpdateView.as_view(), name="ventadetalleproducto-update"),
    path("detalles-productos/<int:pk>/eliminar/", VentaDetalleProductoDeleteView.as_view(), name="ventadetalleproducto-delete"),
    
    # Venta Detalle Servicio URLs
    path("detalles-servicios/", VentaDetalleServicioListView.as_view(), name="ventadetalleservicio-list"),
    path("detalles-servicios/<int:pk>/", VentaDetalleServicioDetailView.as_view(), name="ventadetalleservicio-detail"),
    path("detalles-servicios/crear/", VentaDetalleServicioCreateView.as_view(), name="ventadetalleservicio-create"),
    path("detalles-servicios/<int:pk>/editar/", VentaDetalleServicioUpdateView.as_view(), name="ventadetalleservicio-update"),
    path("detalles-servicios/<int:pk>/eliminar/", VentaDetalleServicioDeleteView.as_view(), name="ventadetalleservicio-delete"),
]
