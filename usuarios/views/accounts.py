from django.contrib import messages
import logging
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from bedesk.models import Profile
from usuarios.forms import CustomUserCreationForm

from integracao_suap.services import autenticar_suap, pegar_dados_aluno

User = get_user_model()


def logar(request):
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
    # Try to obtain SUAP data from session
    suap_data = None
    access = request.session.get('suap_access')
    if access:
        try:
            from integracao_suap.services import pegar_dados_aluno
            suap_data = pegar_dados_aluno(access)
            # adaptar formato para o template: garantir chaves esperadas
            if suap_data and isinstance(suap_data, dict):
                # preferir valores simples e expor raw.dados para acesso detalhado
                suap_data['nome'] = suap_data.get('nome') or (suap_data.get('raw',{}).get('dados',{}).get('nome_usual'))
                suap_data['matricula'] = suap_data.get('matricula') or (suap_data.get('raw',{}).get('dados',{}).get('matricula'))
                raw_d = suap_data.get('raw', {}).get('dados', {})
                suap_data['email'] = suap_data.get('email') or raw_d.get('email')
                suap_data['email_institucional'] = suap_data.get('email_institucional') or raw_d.get('email')
                suap_data['email_pessoal'] = suap_data.get('email_pessoal') or raw_d.get('email_secundario')
                # preferir foto 150x200 se disponível em raw
                if not suap_data.get('foto'):
                    suap_data['foto'] = raw_d.get('url_foto_150x200') or raw_d.get('url_foto_75x100')
        except Exception:
            suap_data = None

    return render(request, "usuarios/user_profile.html", { 'suap_data': suap_data })
