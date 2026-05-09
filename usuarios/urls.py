from django.urls import path

from usuarios.views.accounts import registrar_usuario, user_profile

urlpatterns = [
    path("perfil/", user_profile, name="user_profile"),
    path("registrar/", registrar_usuario, name="registrar_usuario"),
]
