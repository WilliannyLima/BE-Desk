from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
import logging

from integracao_suap.services import pegar_dados_aluno


@login_required
def sincronizar(request):
    """Força a sincronização dos dados do SUAP para o perfil local.

    Usa requests via pegar_dados_aluno (server-side) e atualiza Profile + User.
    """
    access = request.session.get('suap_access')
    if not access:
        messages.error(request, 'Nenhum token SUAP encontrado para sincronização.')
        return redirect('user_profile')

    try:
        dados = pegar_dados_aluno(access)
    except Exception as e:
        logging.getLogger(__name__).exception('Erro ao sincronizar SUAP: %s', e)
        messages.error(request, 'Falha ao consultar SUAP.')
        return redirect('user_profile')

    if not dados:
        messages.error(request, 'Não foi possível obter dados do SUAP.')
        return redirect('user_profile')

    # Atualiza usuário local
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
        logging.getLogger(__name__).exception('Falha ao salvar usuário local')

    # Atualiza profile
    try:
        profile = getattr(user, 'profile')
        if dados.get('matricula'):
            profile.matricula = dados.get('matricula')
            profile.save()
    except Exception:
        logging.getLogger(__name__).exception('Falha ao salvar profile local')

    messages.success(request, 'Dados sincronizados com sucesso.')
    return redirect('user_profile')
