ADMIN_GROUP_NAMES = ("Administrador", "administrador")
EMPLOYEE_GROUP_NAMES = ("Empleado", "empleado")


def is_admin_user(user):
    if not getattr(user, "is_authenticated", False):
        return False
    return bool(
        user.is_superuser
        or user.is_staff
        or user.groups.filter(name__in=ADMIN_GROUP_NAMES).exists()
    )


def is_employee_user(user):
    if not getattr(user, "is_authenticated", False):
        return False
    return bool(user.groups.filter(name__in=EMPLOYEE_GROUP_NAMES).exists())


def user_role(user):
    if is_admin_user(user):
        return "admin"
    if is_employee_user(user):
        return "empleado"
    return None


def user_role_label(user):
    role = user_role(user)
    if role == "admin":
        return "Administrador"
    if role == "empleado":
        return "Empleado"
    return "Sin rol"
