from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse


class RoleLoginFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.group_admin = Group.objects.create(name="Administrador")
        cls.group_employee = Group.objects.create(name="Empleado")

        cls.admin_user = User.objects.create_user(
            username="admin_test",
            password="pass12345",
        )
        cls.admin_user.groups.add(cls.group_admin)

        cls.employee_user = User.objects.create_user(
            username="empleado_test",
            password="pass12345",
        )
        cls.employee_user.groups.add(cls.group_employee)

    def test_menu_principal_publico(self):
        response = self.client.get(reverse("accounts:menu-principal"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Menu principal")

    def test_login_admin_redirige_a_menu_admin(self):
        response = self.client.post(
            reverse("accounts:login-admin"),
            {"username": "admin_test", "password": "pass12345"},
        )
        self.assertRedirects(
            response, reverse("accounts:menu-admin"), fetch_redirect_response=False
        )

    def test_login_empleado_redirige_a_menu_empleado(self):
        response = self.client.post(
            reverse("accounts:login-empleado"),
            {"username": "empleado_test", "password": "pass12345"},
        )
        self.assertRedirects(
            response, reverse("accounts:menu-empleado"), fetch_redirect_response=False
        )

    def test_empleado_no_puede_entrar_a_catalogos(self):
        self.client.login(username="empleado_test", password="pass12345")
        response = self.client.get(reverse("catalogos:dashboard"))
        self.assertRedirects(
            response, reverse("accounts:menu-empleado"), fetch_redirect_response=False
        )

    def test_anonimo_no_puede_entrar_a_ventas(self):
        response = self.client.get(reverse("ventas:dashboard"))
        self.assertRedirects(
            response, reverse("accounts:menu-principal"), fetch_redirect_response=False
        )

    def test_empleado_si_puede_entrar_a_ventas(self):
        self.client.login(username="empleado_test", password="pass12345")
        response = self.client.get(reverse("ventas:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_login_admin_rechaza_usuario_empleado(self):
        response = self.client.post(
            reverse("accounts:login-admin"),
            {"username": "empleado_test", "password": "pass12345"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "no tiene permisos de administrador")
