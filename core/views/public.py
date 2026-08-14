from django.shortcuts import render


def inicio(request):
    return render(request, "core/inicio.html")


def reserva_sucesso(request):
    return render(request, "core/sucesso.html")
