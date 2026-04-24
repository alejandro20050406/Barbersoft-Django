from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError

from .models import Empleado


class EmpleadoAdminForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        required=False,
        label="Usuario",
        help_text="Nombre de usuario para el empleado. Se crea automáticamente al guardar.",
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label="Contraseña",
        help_text="Contraseña para el usuario del empleado. Obligatorio cuando se crea un nuevo empleado.",
    )

    class Meta:
        model = Empleado
        fields = (
            "nombre",
            "apellido",
            "telefono",
            "correo",
            "estado",
            "fecha_ingreso",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["username"].required = False
            self.fields["password"].required = False
        else:
            self.fields["username"].required = True
            self.fields["password"].required = True

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username and User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Ya existe un usuario con ese nombre. Elija otro usuario.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        if not self.instance.pk and (not username or not password):
            raise ValidationError(
                "Para crear el empleado se debe ingresar un usuario y una contraseña."
            )
        return cleaned_data


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    form = EmpleadoAdminForm
    list_display = ("nombre", "apellido", "telefono", "correo", "estado", "fecha_ingreso")
    list_filter = ("estado", "fecha_ingreso", "fecha_registro")
    search_fields = ("nombre", "apellido", "correo", "telefono")
    ordering = ("apellido", "nombre")
    list_per_page = 20
    readonly_fields = ("fecha_registro",)

    fieldsets = (
        ("Datos personales", {
            "fields": ("nombre", "apellido", "telefono", "correo")
        }),
        ("Datos laborales", {
            "fields": ("estado", "fecha_ingreso")
        }),
        ("Cuenta de acceso", {
            "fields": ("username", "password")
        }),
        ("Auditoría", {
            "fields": ("fecha_registro",),
            "classes": ("collapse",)
        }),
    )

    def save_model(self, request, obj, form, change):
        creating = not change
        super().save_model(request, obj, form, change)

        if creating:
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            if username and password:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=obj.correo or "",
                )
                group, _ = Group.objects.get_or_create(name="Empleado")
                user.groups.add(group)
                user.save()
