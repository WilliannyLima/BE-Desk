from django.urls import path
from . import views
# Não precisamos mais do 'auth_views' aqui

urlpatterns = [
    path('crud/', views.tela_ajax, name='crud_ajax'),

    
    path('agendamentos/', views.lista_agendamentos, name='lista_agendamentos'),
    path('agendamentos/criar/', views.criar_agendamento, name='criar_agendamento'),
   
    path('agendamentos/<int:id>/editar/', views.editar_agendamento, name='editar_agendamento'),
    path('agendamentos/<int:id>/deletar/', views.deletar_agendamento, name='deletar_agendamento'),

    path('', views.inicio, name='inicio'),
    path('locais/', views.lista_locais, name='lista_locais'),
    path('sala/<str:nome_sala>/', views.detalhe_sala, name='detalhe_sala'),
    path('sucesso/', views.reserva_sucesso, name='reserva_sucesso'),
    path('agendar/', views.agendar_sala, name='agendar_sala'),
    
    # Gerenciamento de Salas
    path('gerenciar/', views.gerenciar_reservas, name='listar_pendentes'),
    path('gerenciar/aprovar/<int:agendamento_id>/', views.mudar_status_reserva, {'novo_status': 'APROVADO'}, name='aprovar_reserva'),
    path('gerenciar/rejeitar/<int:agendamento_id>/', views.mudar_status_reserva, {'novo_status': 'REJEITADO'}, name='rejeitar_reserva'),
    
    # Recursos
    path('recursos/', views.lista_recursos, name='lista_recursos'),
    path('recursos/reservar/<int:recurso_id>/', views.reservar_recurso, name='reservar_recurso'),
    
    # Gerenciamento de Recursos
    path('gerenciar/recurso/aprovar/<int:reserva_id>/', views.mudar_status_recurso, {'novo_status': 'APROVADO'}, name='aprovar_recurso'),
    path('gerenciar/recurso/rejeitar/<int:reserva_id>/', views.mudar_status_recurso, {'novo_status': 'REJEITADO'}, name='rejeitar_recurso'),

    # Perfil e Reservas do Usuário
    path('perfil/', views.user_profile, name='user_profile'), # <-- A rota que estava quebrando
    path('reservas/', views.lista_reservas, name='lista_reserva'),
    path('reservas/cancelar/<int:agendamento_id>/', views.cancelar_reserva_usuario, name='cancelar_reserva_usuario'),
    
    
    # Cadastro (fica aqui porque é uma view customizada)
    path('registrar/', views.registrar_usuario, name='registrar_usuario'),
    
    # As rotas de logout e password_reset foram removidas
    # porque agora estão no config/urls.py
]