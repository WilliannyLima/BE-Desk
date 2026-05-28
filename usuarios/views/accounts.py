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
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        # 1) Primeiro tentamos autenticar contra o banco local
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Bem-vindo {user.username}!")
            return redirect("inicio")

        # 2) Se não houver usuário local, tentamos autenticar via SUAP
        tokens, err = autenticar_suap(username, password)
        logging.getLogger(__name__).debug('SUAP auth attempt for %s -> %s (err=%s)', username, bool(tokens), err)
        if tokens:
            access = tokens.get('access') if isinstance(tokens, dict) else tokens
        else:
            access = None
            # se houver erro textual do SUAP, registrar e mostrar mensagem amigável
            if err:
                logging.getLogger(__name__).warning('SUAP token error detail: %s', err)
                # se for erro de disponibilidade (resposta HTML/404/503), informar o usuário
                status = err.get('status') if isinstance(err, dict) else None
                if status and int(status) >= 400:
                    messages.error(request, 'Não foi possível conectar ao SUAP (erro {}). Tente novamente mais tarde.'.format(status))
                    return render(request, "registration/login.html")
        dados = pegar_dados_aluno(access)
        logging.getLogger(__name__).debug('SUAP user data for %s -> %s', username, bool(dados))
        if dados:
            # Cria ou atualiza usuário local com os dados do SUAP
            email = (dados.get('email_academico') or dados.get('email_pessoal') or '') if dados else ''
            nome = dados.get('nome') if dados else username

            user, created = User.objects.get_or_create(username=username, defaults={'email': email, 'first_name': nome})
            if not created:
                # Atualiza email/nome se necessário
                changed = False
                if email and user.email != email:
                    user.email = email; changed = True
                if nome and user.first_name != nome:
                    user.first_name = nome; changed = True
                if changed:
                    user.save()

            # Garantir perfil e matrícula
            profile, _ = Profile.objects.get_or_create(user=user)
            if dados and dados.get('matricula'):
                profile.matricula = dados.get('matricula')
                profile.save()

            # Forçar login do usuário local (sem verificar senha local)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            # Salvar token SUAP na sessão para futuras chamadas (store whole payload)
            try:
                request.session['suap_tokens'] = tokens
                if isinstance(tokens, dict) and tokens.get('access'):
                    request.session['suap_access'] = tokens.get('access')
                # garantir que a sessão seja persistida
                try:
                    request.session.save()
                except Exception:
                    pass
            except Exception:
                logging.getLogger(__name__).exception('Falha ao salvar tokens na sessão')
            messages.success(request, f"Bem-vindo {user.username} (via SUAP)!")
            return redirect('inicio')

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
                suap_data['email'] = suap_data.get('email') or (suap_data.get('raw',{}).get('dados',{}).get('email'))
                # preferir foto 150x200 se disponível em raw
                if not suap_data.get('foto'):
                    raw_d = suap_data.get('raw',{}).get('dados',{})
                    suap_data['foto'] = raw_d.get('url_foto_150x200') or raw_d.get('url_foto_75x100')
        except Exception:
            suap_data = None

    return render(request, "usuarios/user_profile.html", { 'suap_data': suap_data })
