from django.urls import path

from core.views.dashboard import gerenciar_reservas, mudar_status_recurso, mudar_status_reserva
from core.views.public import inicio, reserva_sucesso

urlpatterns = [
    path("", inicio, name="inicio"),
    path("sucesso/", reserva_sucesso, name="reserva_sucesso"),
    path("gerenciar/", gerenciar_reservas, name="listar_pendentes"),
    path(
        "gerenciar/aprovar/<int:agendamento_id>/",
        mudar_status_reserva,
        {"novo_status": "APROVADO"},
        name="aprovar_reserva",
    ),
    path(
        "gerenciar/rejeitar/<int:agendamento_id>/",
        mudar_status_reserva,
        {"novo_status": "REJEITADO"},
        name="rejeitar_reserva",
    ),
    path(
        "gerenciar/recurso/aprovar/<int:reserva_id>/",
        mudar_status_recurso,
        {"novo_status": "APROVADO"},
        name="aprovar_recurso",
    ),
    path(
        "gerenciar/recurso/rejeitar/<int:reserva_id>/",
        mudar_status_recurso,
        {"novo_status": "REJEITADO"},
        name="rejeitar_recurso",
    ),
]
