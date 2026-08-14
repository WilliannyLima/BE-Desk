from django.urls import path

from . import views

urlpatterns = [
    path('notificacoes/', views.notificacoes_lista, name='notificacoes_lista'),
    path('notificacoes/api/', views.notificacoes_api, name='notificacoes_api'),
    path('notificacoes/<int:notificacao_id>/lida/', views.marcar_como_lida, name='notificacoes_lida'),
    path('notificacoes/todas-lidas/', views.marcar_todas_lidas, name='notificacoes_todas_lidas'),
]
