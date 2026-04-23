from .roles import is_admin_user, is_employee_user, user_role_label


def role_context(request):
    user = getattr(request, "user", None)
    return {
        "is_admin_user": is_admin_user(user),
        "is_employee_user": is_employee_user(user),
        "rol_actual_label": user_role_label(user),
    }
