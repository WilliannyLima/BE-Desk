from bedesk.models import Agendamento, ReservaRecurso


def notificacoes_pendentes(request):
    total_pendentes = 0

    if request.user.is_authenticated and request.user.is_staff:
        salas_pendentes_count = Agendamento.objects.filter(status="PENDENTE").count()
        recursos_pendentes_count = ReservaRecurso.objects.filter(status="PENDENTE").count()
        total_pendentes = salas_pendentes_count + recursos_pendentes_count

    return {"pendentes_count": total_pendentes}
