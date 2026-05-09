from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from bedesk.models import Agendamento, ReservaRecurso
from usuarios.permissions import is_admin_or_staff

STATUS_GERENCIAVEIS = ["APROVADO", "REJEITADO"]


@login_required
@user_passes_test(is_admin_or_staff)
def gerenciar_reservas(request):
    context = {
        "salas_pendentes": Agendamento.objects.filter(
            status="PENDENTE",
            sala__isnull=False,
        ),
        "recursos_pendentes": ReservaRecurso.objects.filter(status="PENDENTE"),
        "salas_aprovadas": Agendamento.objects.filter(
            status="APROVADO",
            sala__isnull=False,
        ),
        "recursos_aprovados": ReservaRecurso.objects.filter(status="APROVADO"),
    }
    return render(request, "core/gerenciar.html", context)


@user_passes_test(is_admin_or_staff)
@require_POST
def mudar_status_reserva(request, agendamento_id, novo_status):
    if novo_status not in STATUS_GERENCIAVEIS:
        return JsonResponse({"success": False, "erro": "Status inválido"}, status=400)

    reserva = get_object_or_404(Agendamento, pk=agendamento_id)
    reserva.status = novo_status
    reserva.save()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "id": reserva.id,
                "novo_status": reserva.status,
                "usuario": reserva.usuario.username,
            }
        )
    return redirect("listar_pendentes")


@user_passes_test(is_admin_or_staff)
@require_POST
def mudar_status_recurso(request, reserva_id, novo_status):
    reserva = get_object_or_404(ReservaRecurso, pk=reserva_id)

    if novo_status not in STATUS_GERENCIAVEIS:
        messages.error(request, "Status inválido.")
        return redirect("listar_pendentes")

    reserva.status = novo_status
    reserva.save()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "id": reserva.id,
                "novo_status": reserva.status,
                "usuario": reserva.usuario.username,
            }
        )

    if novo_status == "APROVADO":
        messages.success(request, f"Recurso de {reserva.usuario.username} APROVADO!")
    else:
        messages.warning(request, f"Recurso de {reserva.usuario.username} REJEITADO.")

    return redirect("listar_pendentes")
