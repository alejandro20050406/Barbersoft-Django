from django.urls import path

from .views import dashboard

app_name = "catalogos"

urlpatterns = [
    path("", dashboard, name="dashboard"),
]
