from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("recursos/", views.recursos, name="ver_recursos"),
    path('login/', views.login, name="login")
]