from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from bedesk.models import Recurso
from materiais.forms import ReservaRecursoForm


def lista_recursos(request):
    recursos = Recurso.objects.all()
    return render(request, "materiais/lista_recursos.html", {"recursos": recursos})


@login_required
def reservar_recurso(request, recurso_id):
    recurso = get_object_or_404(Recurso, pk=recurso_id)

    if request.method == "POST":
        form = ReservaRecursoForm(request.POST)
        if form.is_valid():
            nova_reserva = form.save(commit=False)
            nova_reserva.usuario = request.user
            nova_reserva.recurso = recurso
            nova_reserva.status = "PENDENTE"
            nova_reserva.save()

            messages.success(
                request,
                f"Seu pedido para '{recurso.nome}' foi enviado e está pendente de aprovação.",
            )
            return redirect("lista_recursos")
    else:
        form = ReservaRecursoForm()

    return render(
        request,
        "materiais/reservar_recurso.html",
        {"form": form, "recurso": recurso},
    )
