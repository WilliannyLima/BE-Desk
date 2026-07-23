from bedesk.models import Agendamento, ReservaRecurso
from notificacoes.models import Notificacao


def notificacoes_pendentes(request):
    total_pendentes = 0
    notificacoes_nao_lidas = 0

    if request.user.is_authenticated:
        notificacoes_nao_lidas = Notificacao.objects.filter(
            destinatario=request.user,
            lida=False,
        ).count()

        if request.user.is_staff:
            salas_pendentes_count = Agendamento.objects.filter(status="PENDENTE").count()
            recursos_pendentes_count = ReservaRecurso.objects.filter(status="PENDENTE").count()
            total_pendentes = salas_pendentes_count + recursos_pendentes_count

    return {
        "pendentes_count": total_pendentes,
        "notificacoes_nao_lidas": notificacoes_nao_lidas,
    }
