from django.urls import path

from usuarios.views.accounts import registrar_usuario, user_profile
from usuarios.api import meu_perfil
from usuarios.views.sync import sincronizar
from usuarios.views.admin_views import (
    admin_dashboard,
    criar_sala,
    editar_sala,
    excluir_sala,
    gerenciar_permissoes,
    criar_postagem,
)

urlpatterns = [
    path("perfil/", user_profile, name="user_profile"),
    path("registrar/", registrar_usuario, name="registrar_usuario"),
    path("api/me/", meu_perfil, name="api_meu_perfil"),
    path("sincronizar/", sincronizar, name="sincronizar_usuario"),
    path("painel-admin/", admin_dashboard, name="admin_dashboard"),
    path("painel-admin/salas/criar/", criar_sala, name="criar_sala"),
    path("painel-admin/salas/<int:pk>/editar/", editar_sala, name="editar_sala"),
    path("painel-admin/salas/<int:pk>/excluir/", excluir_sala, name="excluir_sala"),
    path("painel-admin/permissoes/", gerenciar_permissoes, name="gerenciar_permissoes"),
    path("painel-admin/permissoes/listar/", gerenciar_permissoes, name="gerenciar_permissoes"),
    path("painel-admin/postagem/criar/", criar_postagem, name="criar_postagem"),
]
