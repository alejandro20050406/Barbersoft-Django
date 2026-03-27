from django.contrib import admin
from django.http import HttpResponse
from django.urls import path


def inicio(request):
    return HttpResponse("BarberSoft funcionando correctamente")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", inicio),
]
