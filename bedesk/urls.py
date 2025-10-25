from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('agendar/', views.agendar_sala, name='agendar_sala'),
    path('sucesso/', views.reserva_sucesso, name='reserva_sucesso'), # Este nome é usado no redirect
    path('lista/', views.listar_reservas, name='listar_reservas'),

    # Rotas de Gerenciamento
    path('gerenciar/', views.gerenciar_reservas, name='listar_pendentes'), # Este nome é usado nos redirect('listar_pendentes')
    path('gerenciar/aprovar/<int:agendamento_id>/', 
         views.mudar_status_reserva, {'novo_status': 'APROVADO'}, name='aprovar_reserva'),
    path('gerenciar/rejeitar/<int:agendamento_id>/', 
         views.mudar_status_reserva, {'novo_status': 'REJEITADO'}, name='rejeitar_reserva'),

    # A rota de login deve estar no urls.py principal
]