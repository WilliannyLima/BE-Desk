from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from integracao_suap.services import pegar_dados_aluno
from integracao_suap.services import refresh_token_suap
from integracao_suap.services import autenticar_suap
from django.conf import settings


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
