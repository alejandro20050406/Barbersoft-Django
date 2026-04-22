from django.urls import path

from .views import (
    dashboard,
    # Categoría Producto
    CategoriaProductoListView, CategoriaProductoDetailView,
    CategoriaProductoCreateView, CategoriaProductoUpdateView,
    CategoriaProductoDeleteView,
    # Producto
    ProductoListView, ProductoDetailView,
    ProductoCreateView, ProductoUpdateView,
    ProductoDeleteView,
    # Tipo Servicio
    TipoServicioListView, TipoServicioDetailView,
    TipoServicioCreateView, TipoServicioUpdateView,
    TipoServicioDeleteView,
    # Servicio
    ServicioListView, ServicioDetailView,
    ServicioCreateView, ServicioUpdateView,
    ServicioDeleteView,
    # Método de Pago
    MetodoDePagoListView, MetodoDePagoDetailView,
    MetodoDePagoCreateView, MetodoDePagoUpdateView,
    MetodoDePagoDeleteView,
)

app_name = "catalogos"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    
    # Categoría Producto URLs
    path("categorias/", CategoriaProductoListView.as_view(), name="categoria-list"),
    path("categorias/<int:pk>/", CategoriaProductoDetailView.as_view(), name="categoria-detail"),
    path("categorias/crear/", CategoriaProductoCreateView.as_view(), name="categoria-create"),
    path("categorias/<int:pk>/editar/", CategoriaProductoUpdateView.as_view(), name="categoria-update"),
    path("categorias/<int:pk>/eliminar/", CategoriaProductoDeleteView.as_view(), name="categoria-delete"),
    
    # Producto URLs
    path("productos/", ProductoListView.as_view(), name="producto-list"),
    path("productos/<int:pk>/", ProductoDetailView.as_view(), name="producto-detail"),
    path("productos/crear/", ProductoCreateView.as_view(), name="producto-create"),
    path("productos/<int:pk>/editar/", ProductoUpdateView.as_view(), name="producto-update"),
    path("productos/<int:pk>/eliminar/", ProductoDeleteView.as_view(), name="producto-delete"),
    
    # Tipo Servicio URLs
    path("tipos-servicio/", TipoServicioListView.as_view(), name="tiposervicio-list"),
    path("tipos-servicio/<int:pk>/", TipoServicioDetailView.as_view(), name="tiposervicio-detail"),
    path("tipos-servicio/crear/", TipoServicioCreateView.as_view(), name="tiposervicio-create"),
    path("tipos-servicio/<int:pk>/editar/", TipoServicioUpdateView.as_view(), name="tiposervicio-update"),
    path("tipos-servicio/<int:pk>/eliminar/", TipoServicioDeleteView.as_view(), name="tiposervicio-delete"),
    
    # Servicio URLs
    path("servicios/", ServicioListView.as_view(), name="servicio-list"),
    path("servicios/<int:pk>/", ServicioDetailView.as_view(), name="servicio-detail"),
    path("servicios/crear/", ServicioCreateView.as_view(), name="servicio-create"),
    path("servicios/<int:pk>/editar/", ServicioUpdateView.as_view(), name="servicio-update"),
    path("servicios/<int:pk>/eliminar/", ServicioDeleteView.as_view(), name="servicio-delete"),
    
    # Método de Pago URLs
    path("metodos-pago/", MetodoDePagoListView.as_view(), name="metodopago-list"),
    path("metodos-pago/<int:pk>/", MetodoDePagoDetailView.as_view(), name="metodopago-detail"),
    path("metodos-pago/crear/", MetodoDePagoCreateView.as_view(), name="metodopago-create"),
    path("metodos-pago/<int:pk>/editar/", MetodoDePagoUpdateView.as_view(), name="metodopago-update"),
    path("metodos-pago/<int:pk>/eliminar/", MetodoDePagoDeleteView.as_view(), name="metodopago-delete"),
]
