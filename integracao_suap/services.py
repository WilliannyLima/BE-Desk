import requests
import logging
from django.conf import settings


API_BASE = getattr(settings, 'SUAP_API_URL', 'https://suap.ifrn.edu.br').rstrip('/')
_AUTH_ENDPOINT = None


def obter_token_oauth2(code, redirect_uri, timeout=10):
    """Troca o código de autorização pelo token OAuth2."""
    url = f"{API_BASE}/o/token/"
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': settings.SUAP_OAUTH_CLIENT_ID,
        'client_secret': settings.SUAP_OAUTH_CLIENT_SECRET,
    }
    try:
        res = requests.post(url, data=data, timeout=timeout)
        if res.status_code == 200:
            return res.json(), None
        else:
            return None, {'status': res.status_code, 'text': res.text[:2000]}
    except requests.RequestException as e:
        logging.getLogger(__name__).debug('Erro de conexão no token OAuth2: %s', e)
        return None, {'exception': str(e)}

def autenticar_suap(matricula, password, timeout=8):
    """Autentica no SUAP tentando automaticamente endpoints compatíveis (v2 -> v1).

    Retorna tupla (payload_dict_or_none, error_or_none).
    """
    global _AUTH_ENDPOINT

    candidates = []
    # prefer explicit v2
    candidates.append(f"{API_BASE}/api/v2/autenticacao/token/")
    # legacy v1 token pair
    candidates.append(f"{API_BASE}/api/token/pair")
    candidates.append(f"{API_BASE}/api/token/pair/")
    candidates.append(f"{API_BASE}/api/auth/token/")

    data = {'username': matricula, 'password': password}

    # if we already discovered a working endpoint, try it first
    if _AUTH_ENDPOINT:
        candidates.insert(0, _AUTH_ENDPOINT)

    last_err = None
    for token_url in candidates:
        try:
            res = requests.post(token_url, json=data, timeout=timeout)
        except requests.RequestException as e:
            last_err = {'exception': str(e)}
            logging.getLogger(__name__).debug('Erro de conexão para %s: %s', token_url, e)
            continue

        # sucesso
        if res.status_code == 200:
            try:
                payload = res.json()
            except ValueError:
                last_err = {'status': res.status_code, 'text': res.text[:2000]}
                continue
            # memorize working endpoint
            _AUTH_ENDPOINT = token_url
            return payload, None

        # resposta não 200 -> registrar e tentar próximo
        last_err = {'status': res.status_code, 'text': res.text[:2000]}
        logging.getLogger(__name__).warning('SUAP token endpoint %s retornou %s', token_url, res.status_code)

    return None, last_err


def refresh_token_suap(refresh_token, timeout=8):
    """Renova o token via endpoint v2; retorna novo payload ou None."""
    if not refresh_token:
        return None
    # try v2 refresh then legacy /api/token/refresh
    candidates = [f"{API_BASE}/api/v2/autenticacao/token/refresh/", f"{API_BASE}/api/token/refresh", f"{API_BASE}/api/token/refresh/"]
    for url in candidates:
        try:
            res = requests.post(url, json={'refresh': refresh_token}, timeout=timeout)
        except requests.RequestException:
            continue
        if res.status_code == 200:
            try:
                return res.json()
            except ValueError:
                return None
    return None


def pegar_dados_aluno(access_token, timeout=8):
    """Busca informações do usuário usando os endpoints v2 de "minhas-informacoes".

    Retorna um dict simplificado com chaves comuns (nome, matricula, foto, campus, email, curso, vinculos, raw).
    """
    if not access_token:
        return None

    headers = {'Authorization': f'Bearer {access_token}'}
    result = {}

    # try v2 endpoints first, then legacy endpoints
    dados = {}
    vinculos = {}
    tried = []
    try:
        res_dados = requests.get(f"{API_BASE}/api/v2/minhas-informacoes/meus-dados/", headers=headers, timeout=timeout)
        tried.append(('v2/meus-dados', res_dados.status_code))
        if res_dados.status_code == 200:
            try:
                dados = res_dados.json()
            except ValueError:
                dados = {}
    except requests.RequestException:
        pass

    try:
        res_vinculos = requests.get(f"{API_BASE}/api/v2/minhas-informacoes/meus-vinculos/", headers=headers, timeout=timeout)
        tried.append(('v2/meus-vinculos', res_vinculos.status_code))
        if res_vinculos.status_code == 200:
            try:
                vinculos = res_vinculos.json()
            except ValueError:
                vinculos = {}
    except requests.RequestException:
        pass

    # if v2 calls failed, try legacy endpoints
    if not dados:
        try:
            res_legacy = requests.get(f"{API_BASE}/api/rh/meus-dados/", headers=headers, timeout=timeout)
            tried.append(('legacy/rh/meus-dados', res_legacy.status_code))
            if res_legacy.status_code == 200:
                try:
                    dados = res_legacy.json()
                except ValueError:
                    dados = {}
        except requests.RequestException:
            pass

    if not vinculos:
        try:
            res_legacy_v = requests.get(f"{API_BASE}/api/rh/meus-vinculos/", headers=headers, timeout=timeout)
            tried.append(('legacy/rh/meus-vinculos', res_legacy_v.status_code))
            if res_legacy_v.status_code == 200:
                try:
                    vinculos = res_legacy_v.json()
                except ValueError:
                    vinculos = {}
        except requests.RequestException:
            pass

    # if both empty, give up
    if not dados and not vinculos:
        logging.getLogger(__name__).warning('Falha ao obter dados SUAP, tentativas: %s', tried)
        return None

    # Mapeamento preferencial para o endpoint v2 /meus-dados/
    nome = dados.get('nome_usual') or dados.get('nome') or dados.get('nome_registro') or dados.get('nome_completo')
    matricula = dados.get('matricula') or dados.get('identificacao') or dados.get('siape') or dados.get('siape_matricula')
    # v2 costuma usar 'email' ou 'email_academico'
    email = dados.get('email') or dados.get('email_academico') or dados.get('email_pessoal') or dados.get('email_secundario')

    # fotos no v2 estão em campos específicos (ex: url_foto_150x200)
    foto = None
    for key in ('url_foto_150x200', 'url_foto_75x100', 'url_foto'):
        if isinstance(dados.get(key), str) and dados.get(key):
            foto = dados.get(key)
            break
    # também aceitar campos genéricos
    if not foto:
        foto = dados.get('foto') or dados.get('url_foto')

    # tentar extrair curso/campus/vinculo a partir de vinculos
    curso = None
    campus = None
    tipo_vinculo = None
    if isinstance(vinculos, dict):
        # alguns endpoints retornam {'results': [...]}
        items = vinculos.get('results', vinculos if isinstance(vinculos, list) else [])
    else:
        items = vinculos if isinstance(vinculos, list) else []

    if items:
        # pega o primeiro vínculo como resumo
        v = items[0] if isinstance(items, list) else items
        # v2 frequentemente embute detalhes em 'detalhamento'
        detalhamento = v.get('detalhamento') if isinstance(v, dict) else None
        detalhe = detalhamento if isinstance(detalhamento, dict) else None
        curso = (detalhe.get('curso') if detalhe else None) or v.get('curso') or v.get('nome_curso')
        campus = v.get('campus') or v.get('nome_campus') or (detalhe.get('campus') if detalhe else None)
        tipo_vinculo = v.get('tipo') or v.get('tipo_vinculo') or v.get('vinculo')

    usuario = {
        'nome': nome,
        'matricula': matricula,
        'email': email,
        'foto': foto,
        'curso': curso,
        'campus': campus,
        'vinculos': items,
        'tipo_vinculo': tipo_vinculo,
        'raw': {'dados': dados, 'vinculos': vinculos}
    }

    # Normalizar foto absoluta
    if usuario['foto'] and isinstance(usuario['foto'], str) and usuario['foto'].startswith('/'):
        usuario['foto'] = API_BASE + usuario['foto']

    return usuario
