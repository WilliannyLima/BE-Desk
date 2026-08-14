from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from integracao_suap.services import pegar_dados_aluno
from integracao_suap.services import refresh_token_suap
from integracao_suap.services import autenticar_suap
from django.conf import settings
import urllib.parse
from django.shortcuts import redirect
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from bedesk.models import Profile
from integracao_suap.services import obter_token_oauth2, API_BASE


def suap_login(request):
    url = (
        f"{settings.SUAP_BASE_URL}/o/authorize/"
        f"?response_type=code"
        f"&client_id={settings.SUAP_OAUTH_CLIENT_ID}"
        f"&redirect_uri={settings.SUAP_OAUTH_REDIRECT_URI}"
    )
    return redirect(url)


@login_required
def debug_token(request):
    # Debug helper: returns session stored SUAP tokens when DEBUG is True
    if not settings.DEBUG:
        return JsonResponse({'ok': False, 'error': 'disabled'}, status=403)
    return JsonResponse({'ok': True, 'suap_tokens': request.session.get('suap_tokens'), 'suap_access': request.session.get('suap_access')})


@login_required
def rh_eu(request):
    access = request.session.get('suap_access')
    if not access:
        return JsonResponse({'ok': False, 'error': 'no_token'}, status=401)

    dados = pegar_dados_aluno(access)
    if dados is None:
        # Try to refresh token if we have refresh token saved
        tokens = request.session.get('suap_tokens') or {}
        refresh = tokens.get('refresh') if isinstance(tokens, dict) else None
        if refresh:
            new_payload = refresh_token_suap(refresh)
            if new_payload and isinstance(new_payload, dict) and new_payload.get('access'):
                # update session
                request.session['suap_tokens'] = new_payload
                request.session['suap_access'] = new_payload.get('access')
                dados = pegar_dados_aluno(new_payload.get('access'))
            else:
                logging.getLogger(__name__).warning('Falha ao renovar token SUAP com refresh: %s', bool(new_payload))
    # If still no dados, maybe session tokens not present: try to use POST credentials in request.POST (debug only)
    if dados is None and settings.DEBUG:
        # permitir autenticar via body (apenas dev) para testes rápidos
        matricula = request.POST.get('debug_matricula')
        senha = request.POST.get('debug_senha')
        if matricula and senha:
            tokens, err = autenticar_suap(matricula, senha)
            if tokens:
                request.session['suap_tokens'] = tokens
                request.session['suap_access'] = tokens.get('access') if isinstance(tokens, dict) else tokens
                dados = pegar_dados_aluno(request.session.get('suap_access'))

    if not dados:
        return JsonResponse({'ok': False, 'error': 'suap_error'}, status=502)

    return JsonResponse({'ok': True, 'data': dados})


def suap_login_oauth(request):
    """Redireciona o usuário para a página de autorização do SUAP."""
    client_id = settings.SUAP_OAUTH_CLIENT_ID
    redirect_uri = settings.SUAP_OAUTH_REDIRECT_URI
    authorize_url = f"{API_BASE}/o/authorize/"
    
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
    }
    url = f"{authorize_url}?{urllib.parse.urlencode(params)}"
    return redirect(url)


def suap_callback(request):
    """Recebe o código do SUAP, troca por token e autentica o usuário."""
    code = request.GET.get('code')
    error = request.GET.get('error')

    if error:
        messages.error(request, f"Erro na autorização: {error}")
        return redirect('login')
    
    if not code:
        messages.error(request, "Código de autorização não recebido.")
        return redirect('login')

    tokens, err = obter_token_oauth2(code, settings.SUAP_OAUTH_REDIRECT_URI)
    
    if not tokens or err:
        messages.error(request, "Falha ao obter token do SUAP.")
        return redirect('login')

    access = tokens.get('access_token') or tokens.get('access')
    if not access:
        messages.error(request, "Token de acesso inválido.")
        return redirect('login')

    # Busca os dados do usuário
    dados = pegar_dados_aluno(access)
    
    if not dados:
        messages.error(request, "Não foi possível carregar os dados do usuário do SUAP.")
        return redirect('login')

    User = get_user_model()
    username = dados.get('matricula')
    if not username:
        messages.error(request, "Matrícula não encontrada nos dados do SUAP.")
        return redirect('login')

    email = dados.get('email') or ''
    nome = dados.get('nome') or username

    user, created = User.objects.get_or_create(username=username, defaults={'email': email, 'first_name': nome})
    if not created:
        changed = False
        if email and user.email != email:
            user.email = email
            changed = True
        if nome and user.first_name != nome:
            user.first_name = nome
            changed = True
        if changed:
            user.save()

    profile, _ = Profile.objects.get_or_create(user=user)
    if dados.get('matricula'):
        profile.matricula = dados.get('matricula')
        profile.save()

    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    
    # Salvar token na sessão
    try:
        request.session['suap_tokens'] = tokens
        request.session['suap_access'] = access
        request.session.save()
    except Exception:
        pass
        
    messages.success(request, f"Bem-vindo {user.username}!")
    return redirect('inicio')
