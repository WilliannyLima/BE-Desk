from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('agendar/', views.agendar_sala, name='agendar_sala'),
    path('sucesso/', views.reserva_sucesso, name='reserva_sucesso'), # Este nome é usado no redirect
   

    # Rotas de Gerenciamento
    path('gerenciar/', views.gerenciar_reservas, name='listar_pendentes'), # Este nome é usado nos redirect('listar_pendentes')
    path('gerenciar/aprovar/<int:agendamento_id>/', views.mudar_status_reserva, {'novo_status': 'APROVADO'}, name='aprovar_reserva'),
    path('gerenciar/rejeitar/<int:agendamento_id>/', views.mudar_status_reserva, {'novo_status': 'REJEITADO'}, name='rejeitar_reserva'),
    path('recursos/', views.lista_recursos, name='lista_recursos'),
    path('recursos/reservar/<int:recurso_id>/', views.reservar_recurso, name='reservar_recurso'),

# --- PERFIL DO USUÁRIO ---
    path('perfil/', views.user_profile, name='user_profile'),

# --- NOVAS LINHAS PARA OS RECURSOS ---
    path('gerenciar/recurso/aprovar/<int:reserva_id>/', views.mudar_status_recurso, {'novo_status': 'APROVADO'}, name='aprovar_recurso'),
    path('gerenciar/recurso/rejeitar/<int:reserva_id>/', views.mudar_status_recurso, {'novo_status': 'REJEITADO'}, name='rejeitar_recurso'),
    # A rota de login deve estar no urls.py principal
    
     path('reservas/', views.lista_reservas, name='lista_reserva'),
    path('reservas/cancelar/<int:agendamento_id>/', views.cancelar_reserva_usuario, name='cancelar_reserva_usuario'),
    path('reservas/excluir/<int:agendamento_id>/', views.excluir_reserva_usuario, name='excluir_reserva_usuario'),
    path('logout/', views.log_out, name='logout'),
    
    path('registrar/', views.registrar_usuario, name='registrar_usuario'),
     path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]