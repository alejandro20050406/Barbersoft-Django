from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from apps.catalogos.models import CategoriaProducto, MetodoDePago, Producto, Servicio
from apps.clientes.models import Cliente
from apps.empleados.models import Empleado
from apps.ventas.models import Venta

from .forms import LoginForm
from .roles import is_admin_user, is_employee_user


def menu_principal(request):
    if request.user.is_authenticated:
        return redirect(_menu_por_usuario(request.user))
    return render(request, "accounts/menu_principal.html")


def login_admin(request):
    return _login_por_rol(request, rol="admin")


def login_empleado(request):
    return _login_por_rol(request, rol="empleado")


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Sesion cerrada correctamente.")
    return redirect("accounts:menu-principal")


def menu_admin(request):
    if not request.user.is_authenticated:
        return redirect("accounts:menu-principal")
    if not is_admin_user(request.user):
        messages.error(request, "Solo administradores pueden entrar al menu admin.")
        return redirect(_menu_por_usuario(request.user))
    return render(request, "accounts/menu_admin.html")


def menu_empleado(request):
    if not request.user.is_authenticated:
        return redirect("accounts:menu-principal")
    if is_admin_user(request.user):
        return redirect("accounts:menu-admin")
    if not is_employee_user(request.user):
        messages.error(request, "Tu usuario no tiene rol de empleado.")
        logout(request)
        return redirect("accounts:menu-principal")
    return render(request, "accounts/menu_empleado.html")


def home(request):
    if not request.user.is_authenticated:
        return redirect("accounts:menu-principal")
    if not is_admin_user(request.user):
        return redirect("accounts:menu-empleado")

    stats = {
        "categorias": CategoriaProducto.objects.count(),
        "metodos_pago": MetodoDePago.objects.count(),
        "productos": Producto.objects.count(),
        "servicios": Servicio.objects.count(),
        "clientes": Cliente.objects.count(),
        "empleados": Empleado.objects.count(),
        "ventas": Venta.objects.count(),
    }
    return render(request, "accounts/home.html", {"stats": stats})


def _login_por_rol(request, rol):
    if request.user.is_authenticated:
        return redirect(_menu_por_usuario(request.user))

    form = LoginForm(request.POST or None)
    es_admin = rol == "admin"
    titulo = "Inicio de sesion como Administrador" if es_admin else "Inicio de sesion como Empleado"

    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Usuario o contraseña incorrectos.")
        elif es_admin and not is_admin_user(user):
            messages.error(request, "Ese usuario no tiene permisos de administrador.")
        elif not es_admin and not is_employee_user(user):
            messages.error(request, "Ese usuario no tiene permisos de empleado.")
        else:
            login(request, user)
            return redirect("accounts:menu-admin" if es_admin else "accounts:menu-empleado")

    return render(
        request,
        "accounts/login.html",
        {
            "form": form,
            "titulo_login": titulo,
            "es_admin": es_admin,
        },
    )


def _menu_por_usuario(user):
    if is_admin_user(user):
        return "accounts:menu-admin"
    return "accounts:menu-empleado"
