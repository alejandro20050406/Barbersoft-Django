import re

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError

from .models import Empleado


class EmpleadoForm(forms.ModelForm):
    username = forms.CharField(
        required=False,
        label="Usuario",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        help_text="Nombre de usuario que tendrá el empleado para ingresar a la plataforma.",
    )
    password = forms.CharField(
        required=False,
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text="Contraseña para el empleado.",
    )

    class Meta:
        model = Empleado
        fields = [
            "nombre",
            "apellido",
            "telefono",
            "correo",
            "estado",
            "fecha_ingreso",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "apellido": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "3121234567",
                    "maxlength": "10",
                    "minlength": "10",
                    "inputmode": "numeric",
                    "pattern": r"\d{10}",
                    "title": "Ingresa exactamente 10 dígitos",
                }
            ),
            "correo": forms.EmailInput(attrs={"class": "form-control"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "fecha_ingreso": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"class": "form-control", "type": "date"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fecha_ingreso"].input_formats = ["%Y-%m-%d"]
        self.fields["telefono"].required = True
        self.fields["telefono"].widget.attrs["required"] = "required"

        usuario = getattr(self.instance, "usuario", None)
        if usuario:
            self.fields["username"].initial = usuario.username
            self.fields["password"].help_text = (
                "Déjala en blanco para conservar la contraseña actual."
            )

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "").strip()
        if not nombre:
            raise ValidationError("El nombre no puede estar vacío.")
        if len(nombre) < 2:
            raise ValidationError("El nombre debe tener al menos 2 caracteres.")
        if any(char.isdigit() for char in nombre):
            raise ValidationError("El nombre no puede contener números.")
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+$", nombre):
            raise ValidationError(
                "El nombre solo puede contener letras y espacios, sin signos especiales."
            )
        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get("apellido", "").strip()
        if not apellido:
            raise ValidationError("El apellido es obligatorio.")
        if len(apellido) < 2:
            raise ValidationError("El apellido debe tener al menos 2 caracteres.")
        if any(char.isdigit() for char in apellido):
            raise ValidationError("El apellido no puede contener números.")
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+$", apellido):
            raise ValidationError(
                "El apellido solo puede contener letras y espacios, sin signos especiales."
            )
        return apellido

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono", "")
        if not telefono:
            raise ValidationError("El teléfono es obligatorio.")
        telefono_limpio = re.sub(r"\D", "", telefono.strip())
        if len(telefono_limpio) != 10:
            raise ValidationError("Número de teléfono inválido. Debe tener exactamente 10 dígitos.")
        return telefono_limpio

    def clean_correo(self):
        correo = self.cleaned_data.get("correo", "")
        if not correo:
            return correo

        correo = correo.strip().lower()
        qs = Empleado.objects.filter(correo__iexact=correo)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe un empleado con ese correo.")
        return correo

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()
        if not username and not self.instance.pk:
            raise ValidationError("El usuario es obligatorio para crear el empleado.")

        qs = User.objects.filter(username__iexact=username)
        usuario_actual = getattr(self.instance, "usuario", None)
        if usuario_actual:
            qs = qs.exclude(pk=usuario_actual.pk)
        if username and qs.exists():
            raise ValidationError("Ya existe un usuario con ese nombre.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get("password", "")
        if not password and not self.instance.pk:
            raise ValidationError("La contraseña es obligatoria para crear el empleado.")
        return password

    def _password_validation_user(self, username):
        usuario = getattr(self.instance, "usuario", None) or User()
        usuario.username = username or ""
        usuario.email = self.cleaned_data.get("correo") or ""
        usuario.first_name = self.cleaned_data.get("nombre") or ""
        usuario.last_name = self.cleaned_data.get("apellido") or ""
        return usuario

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        usuario_actual = getattr(self.instance, "usuario", None)

        if username and not usuario_actual and not password:
            self.add_error(
                "password",
                "La contraseña es obligatoria para crear la cuenta de acceso.",
            )
        if password and not username:
            self.add_error(
                "username",
                "Ingresa un usuario para poder guardar la contraseña.",
            )
        if password:
            try:
                validate_password(password, self._password_validation_user(username))
            except ValidationError as error:
                self.add_error("password", error)
        return cleaned_data

    def clean_fecha_ingreso(self):
        fecha_ingreso = self.cleaned_data.get("fecha_ingreso")
        if fecha_ingreso is None:
            raise ValidationError("La fecha de ingreso es obligatoria.")
        return fecha_ingreso

    def save(self, commit=True):
        empleado = super().save(commit=commit)

        if commit:
            username = self.cleaned_data.get("username")
            password = self.cleaned_data.get("password")
            user = getattr(empleado, "usuario", None)

            if username:
                if user is None:
                    user = User.objects.create_user(username=username)
                else:
                    user.username = username

                user.email = empleado.correo or ""
                user.first_name = empleado.nombre
                user.last_name = empleado.apellido
                if password:
                    user.set_password(password)
                user.save()

                group, _ = Group.objects.get_or_create(name="Empleado")
                user.groups.add(group)

                if empleado.usuario_id != user.id:
                    empleado.usuario = user
                    empleado.save(update_fields=["usuario"])

        return empleado
