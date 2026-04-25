from datetime import date, datetime

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


FUTURE_DATE_ERROR = (
    "No se permiten fechas futuras. La fecha maxima permitida es la fecha actual."
)


def _today():
    return timezone.localdate()


def _today_iso():
    return _today().isoformat()


def _limit_max_attr(attrs, max_value):
    current_max = attrs.get("max")
    if not current_max or current_max > max_value:
        attrs["max"] = max_value


def _date_part(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        if timezone.is_aware(value):
            return timezone.localtime(value).date()
        return value.date()
    if isinstance(value, date):
        return value
    return None


def _validate_not_future(value):
    value_date = _date_part(value)
    if value_date is not None and value_date > _today():
        raise ValidationError(FUTURE_DATE_ERROR, code="future_date")


def apply_future_date_limit():
    if getattr(forms.DateField, "_barbersoft_future_limit", False):
        return

    original_form_date_validate = forms.DateField.validate
    original_form_datetime_validate = forms.DateTimeField.validate
    original_model_date_validate = models.DateField.validate
    original_model_datetime_validate = models.DateTimeField.validate
    original_date_input_get_context = forms.DateInput.get_context
    original_datetime_input_get_context = forms.DateTimeInput.get_context

    def form_date_validate(self, value):
        original_form_date_validate(self, value)
        _validate_not_future(value)

    def form_datetime_validate(self, value):
        original_form_datetime_validate(self, value)
        _validate_not_future(value)

    def model_date_validate(self, value, model_instance):
        original_model_date_validate(self, value, model_instance)
        _validate_not_future(value)

    def model_datetime_validate(self, value, model_instance):
        original_model_datetime_validate(self, value, model_instance)
        _validate_not_future(value)

    def date_input_get_context(self, name, value, attrs):
        context = original_date_input_get_context(self, name, value, attrs)
        widget = context["widget"]
        attrs = widget.setdefault("attrs", {})
        if widget.get("type") == "date":
            _limit_max_attr(attrs, _today_iso())
        return context

    def datetime_input_get_context(self, name, value, attrs):
        context = original_datetime_input_get_context(self, name, value, attrs)
        widget = context["widget"]
        attrs = widget.setdefault("attrs", {})
        if widget.get("type") == "datetime-local":
            _limit_max_attr(attrs, timezone.localtime().strftime("%Y-%m-%dT%H:%M"))
        return context

    forms.DateField.validate = form_date_validate
    forms.DateTimeField.validate = form_datetime_validate
    models.DateField.validate = model_date_validate
    models.DateTimeField.validate = model_datetime_validate
    forms.DateInput.get_context = date_input_get_context
    forms.DateTimeInput.get_context = datetime_input_get_context

    forms.DateField._barbersoft_future_limit = True
