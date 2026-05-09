import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from bedesk.models import Agendamento, Sala


def lista_agendamentos(request):
    dados = Agendamento.objects.all().values("id", "nome", "motivo", "status")
    return JsonResponse(list(dados), safe=False)


@csrf_exempt
def criar_agendamento(request):
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    data = json.loads(request.body)
    sala = Sala.objects.first()

    Agendamento.objects.create(
        nome=data.get("nome"),
        motivo=data.get("motivo"),
        sala=sala,
        usuario=request.user,
    )

    return JsonResponse({"status": "criado"})


@csrf_exempt
def editar_agendamento(request, id):
    if request.method != "PUT":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    data = json.loads(request.body)
    agendamento = get_object_or_404(Agendamento, id=id)
    agendamento.nome = data.get("nome")
    agendamento.motivo = data.get("motivo")
    agendamento.save()

    return JsonResponse({"status": "editado"})


@csrf_exempt
def deletar_agendamento(request, id):
    if request.method != "DELETE":
        return JsonResponse({"erro": "Método não permitido"}, status=405)

    agendamento = get_object_or_404(Agendamento, id=id)
    agendamento.delete()

    return JsonResponse({"status": "deletado"})


def tela_ajax(request):
    return render(request, "reservas/agendamentos_ajax.html")
