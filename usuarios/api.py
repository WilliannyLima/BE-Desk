from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from integracao_suap.services import pegar_dados_aluno
from django.shortcuts import redirect
from django.contrib import messages


@login_required
def meu_perfil(request):
    # Tenta obter dados do SUAP a partir do token salvo na sessão
    access = request.session.get('suap_access')
    dados = None
    if access:
        dados = pegar_dados_aluno(access)

    # fallback: preencher com dados locais
    if not dados:
        user = request.user
        dados = {
            'nome': user.first_name or user.get_full_name() or user.username,
            'matricula': getattr(user, 'username', ''),
            'email': user.email,
            'foto': None,
        }

    # incluir informações adicionais locais (perfil)
    profile = getattr(request.user, 'profile', None)
    if profile:
        dados['matricula'] = dados.get('matricula') or profile.matricula

    return JsonResponse({'ok': True, 'data': dados})


@login_required
def sincronizar(request):
    access = request.session.get('suap_access')
    if not access:
        return JsonResponse({'ok': False, 'error': 'no_token'})
    dados = pegar_dados_aluno(access)
    if not dados:
        return JsonResponse({'ok': False, 'error': 'no_data'})
    # atualiza profile local como no sincronizar view
    user = request.user
    nome = dados.get('nome')
    email = dados.get('email')
    if nome and user.first_name != nome:
        user.first_name = nome
    if email and user.email != email:
        user.email = email
    try:
        user.save()
    except Exception:
        pass
    profile = getattr(user, 'profile', None)
    if profile and dados.get('matricula'):
        profile.matricula = dados.get('matricula')
        profile.save()
    return JsonResponse({'ok': True})
