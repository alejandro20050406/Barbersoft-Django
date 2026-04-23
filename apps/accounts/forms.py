from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Usuario",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": "usuario",
                "class": "form-control",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="Contrasena",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "********",
                "class": "form-control",
                "autocomplete": "current-password",
            }
        ),
    )
