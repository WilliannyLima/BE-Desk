from django.urls import path

from usuarios.views.accounts import registrar_usuario, user_profile
from usuarios.api import meu_perfil
from usuarios.views.sync import sincronizar

urlpatterns = [
    path("perfil/", user_profile, name="user_profile"),
    path("registrar/", registrar_usuario, name="registrar_usuario"),
    path("api/me/", meu_perfil, name="api_meu_perfil"),
    path("sincronizar/", sincronizar, name="sincronizar_usuario"),
]
