from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from bedesk.models import Profile
from usuarios.forms import CustomUserCreationForm


def logar(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Bem-vindo {user.username}!")
            return redirect("inicio")

        messages.error(request, "Usuário ou senha inválidos.")

    return render(request, "registration/login.html")


def log_out(request):
    logout(request)
    return redirect("inicio")


def registrar_usuario(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário registrado com sucesso! Faça login.")
            return redirect("login")
    else:
        form = CustomUserCreationForm()

    return render(request, "usuarios/registrar_usuario.html", {"form": form})


@login_required
def user_profile(request):
    Profile.objects.get_or_create(user=request.user)
    return render(request, "usuarios/user_profile.html")
