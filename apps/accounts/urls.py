from django.urls import path

from .views import (
    home,
    login_admin,
    login_empleado,
    logout_view,
    menu_admin,
    menu_empleado,
    menu_principal,
)

app_name = "accounts"

urlpatterns = [
    path("", menu_principal, name="menu-principal"),
    path("login/administrador/", login_admin, name="login-admin"),
    path("login/empleado/", login_empleado, name="login-empleado"),
    path("logout/", logout_view, name="logout"),
    path("menu/administrador/", menu_admin, name="menu-admin"),
    path("menu/empleado/", menu_empleado, name="menu-empleado"),
    path("inicio/", home, name="home"),
]
