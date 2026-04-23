from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse

from .roles import is_admin_user, is_employee_user, user_role


class RoleAccessMiddleware:
    """
    Controla acceso global por autenticacion y rol:
    - publico: menu principal y login por rol
    - admin: catalogos, empleados, clientes, reportes, inicio administrativo
    - empleado: ventas y su menu
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if self._is_static_or_django_admin(path):
            return self.get_response(request)

        public_paths = {
            reverse("accounts:menu-principal"),
            reverse("accounts:login-admin"),
            reverse("accounts:login-empleado"),
            reverse("accounts:logout"),
        }

        if path in public_paths:
            if request.user.is_authenticated and path != reverse("accounts:logout"):
                return redirect(self._menu_for(request.user))
            return self.get_response(request)

        if not request.user.is_authenticated:
            return redirect("accounts:menu-principal")

        role = user_role(request.user)
        if role is None:
            logout(request)
            messages.error(
                request,
                "Tu usuario no tiene un rol asignado. Solicita acceso al administrador.",
            )
            return redirect("accounts:menu-principal")

        if path.startswith(reverse("accounts:menu-admin")) and not is_admin_user(
            request.user
        ):
            messages.error(
                request, "Solo los administradores pueden entrar a ese menu."
            )
            return redirect("accounts:menu-empleado")

        if path.startswith(reverse("accounts:menu-empleado")) and is_admin_user(
            request.user
        ):
            return redirect("accounts:menu-admin")

        if path.startswith(reverse("accounts:home")) and not is_admin_user(request.user):
            return redirect("accounts:menu-empleado")

        admin_only_prefixes = (
            "/catalogos/",
            "/clientes/",
            "/empleados/",
            "/reportes/",
        )
        if any(path.startswith(prefix) for prefix in admin_only_prefixes) and not is_admin_user(
            request.user
        ):
            messages.error(
                request, "No tienes permisos para ese modulo administrativo."
            )
            return redirect("accounts:menu-empleado")

        return self.get_response(request)

    @staticmethod
    def _is_static_or_django_admin(path):
        return (
            path.startswith("/static/")
            or path.startswith("/media/")
            or path.startswith("/admin/")
        )

    @staticmethod
    def _menu_for(user):
        if is_admin_user(user):
            return reverse("accounts:menu-admin")
        return reverse("accounts:menu-empleado")
