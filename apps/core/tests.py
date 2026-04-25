from datetime import timedelta

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.test import SimpleTestCase, TestCase
from django.utils import timezone


class FutureDateLimitFormTests(SimpleTestCase):
    def test_date_field_rejects_future_date(self):
        class ExampleForm(forms.Form):
            fecha = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

        tomorrow = timezone.localdate() + timedelta(days=1)
        form = ExampleForm(data={"fecha": tomorrow.isoformat()})

        self.assertFalse(form.is_valid())
        self.assertIn("fecha", form.errors)

    def test_date_input_renders_max_today(self):
        class ExampleForm(forms.Form):
            fecha = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

        rendered = str(ExampleForm()["fecha"])

        self.assertIn(f'max="{timezone.localdate().isoformat()}"', rendered)


class FutureDateLimitModelTests(TestCase):
    def test_model_date_field_rejects_future_date_on_full_clean(self):
        field = models.DateField()
        tomorrow = timezone.localdate() + timedelta(days=1)

        with self.assertRaises(ValidationError):
            field.clean(tomorrow, None)
