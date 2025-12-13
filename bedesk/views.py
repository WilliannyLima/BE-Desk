from django.shortcuts import render, redirect, get_object_or_404
from .forms import AgendarForm, ReservaRecursoForm, CustomUserCreationForm
from .models import Sala, Agendamento, Recurso, ReservaRecurso, Profile
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth import logout, authenticate, login
from datetime import datetime, timedelta
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime, timedelta, date


def inicio(request):
    # Esta view agora só renderiza a página de boas-vindas
    return render(request, 'bedesk/inicio.html')

@login_required
def lista_locais(request):
    """
    Esta view busca todas as salas cadastradas (Ginásio, E05, etc.)
    e as envia para um novo template.
    """
    # Busca todas as salas no banco de dados
    locais = Sala.objects.all().order_by('nome')
    
    context = {
        'locais': locais
    }
    return render(request, 'bedesk/lista_locais.html', context)


def detalhe_sala(request, nome_sala):
    
    # --- ESTRUTURA DE HORÁRIOS (garantindo que esteja aqui) ---
    horarios_estrutura = [
        {'tipo': 'separador', 'nome': 'Manhã'},
        {'tipo': 'hora', 'inicio': '07:00', 'fim': '07:45'},
        {'tipo': 'hora', 'inicio': '07:45', 'fim': '08:30'},
        {'tipo': 'intervalo', 'inicio': '08:30', 'fim': '08:50', 'nome': 'Intervalo (20 min)'},
        {'tipo': 'hora', 'inicio': '08:50', 'fim': '09:35'},
        {'tipo': 'hora', 'inicio': '09:35', 'fim': '10:20'},
        {'tipo': 'intervalo', 'inicio': '10:20', 'fim': '10:30', 'nome': 'Intervalo (10 min)'},
        {'tipo': 'hora', 'inicio': '10:30', 'fim': '11:15'},
        {'tipo': 'hora', 'inicio': '11:15', 'fim': '12:00'},
        {'tipo': 'separador', 'nome': 'Tarde'},
        {'tipo': 'hora', 'inicio': '13:00', 'fim': '13:45'},
        {'tipo': 'hora', 'inicio': '13:45', 'fim': '14:30'},
        {'tipo': 'intervalo', 'inicio': '14:30', 'fim': '14:50', 'nome': 'Intervalo (20 min)'},
        {'tipo': 'hora', 'inicio': '14:50', 'fim': '15:35'},
        {'tipo': 'hora', 'inicio': '15:35', 'fim': '16:20'},
        {'tipo': 'intervalo', 'inicio': '16:20', 'fim': '16:30', 'nome': 'Intervalo (10 min)'},
        {'tipo': 'hora', 'inicio': '16:30', 'fim': '17:15'},
        {'tipo': 'hora', 'inicio': '17:15', 'fim': '18:00'},
    ]
    dias_semana_nomes = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira']
    # ------------------------------------------------------------------

    # --- NOVO: LÓGICA PARA NAVEGAR ENTRE SEMANAS E DEFINIR O FOCO ---
    data_foco_str = request.GET.get('foco')
    today = date.today()
    
    if data_foco_str:
        try:
            data_foco = datetime.strptime(data_foco_str, '%Y-%m-%d').date()
        except ValueError:
            data_foco = today
    else:
        data_foco = today

    # Início da semana atual (sempre Segunda-feira)
    start_of_current_week = today - timedelta(days=today.weekday())

    # 1. Calcula o início da semana exibida
    start_of_week = data_foco - timedelta(days=data_foco.weekday())
    
    # 2. Define os limites de navegação permitidos
    start_of_previous_week_limit = start_of_current_week - timedelta(days=7)
    start_of_next_week_limit = start_of_current_week + timedelta(days=7)

    # 3. Calcula os alvos de navegação (o link real)
    semana_anterior = start_of_week - timedelta(days=7)
    proxima_semana = start_of_week + timedelta(days=7)
    
    # 4. Determina o status de desativação dos botões
    disable_semana_anterior = (start_of_week <= start_of_previous_week_limit)
    disable_proxima_semana = (start_of_week >= start_of_next_week_limit)


    # 5. Define o status da semana em relação a hoje (para bloqueio de agendamento)
    if start_of_week < start_of_current_week:
        status_semana = 'PASSADA'
    else:
        status_semana = 'FUTURA' 
    # --- FIM DA LÓGICA DE NAVEGAÇÃO ---


    # 2. Busca a sala específica (E05 ou Ginásio)
    try:
        sala_obj = get_object_or_404(Sala, nome__iexact=nome_sala) 
    except Sala.DoesNotExist:
        messages.error(request, f"A sala '{nome_sala}' não foi encontrada.")
        return redirect('inicio')

    # 3. Busca os agendamentos APENAS desta sala
    dias_semana_datas = [start_of_week + timedelta(days=i) for i in range(5)]

    agendamentos = Agendamento.objects.filter(
        sala=sala_obj,
        status='APROVADO',
        data_inicio__date__range=[start_of_week, dias_semana_datas[-1]]
    ).select_related('usuario')

    # 4. Mapeia os agendamentos (lógica anterior)
    agendamentos_map = {}
    for ag in agendamentos:
        hora_str = ag.horario.strftime("%H:%M")
        dia_weekday = ag.data_inicio.weekday()
        agendamentos_map[(hora_str, dia_weekday)] = ag

    # 5. Constrói a tabela (lógica anterior)
    tabela_horarios = []
    for item in horarios_estrutura:
        if item['tipo'] != 'hora':
            tabela_horarios.append(item)
            continue
        
        hora_inicio_str = item['inicio']
        linha = {
            'tipo': 'hora',
            'horario_str': f"{item['inicio']} às {item['fim']}",
            'hora_para_link': hora_inicio_str,
            'celulas': []
        }
        
        for dia_num, data_do_dia in enumerate(dias_semana_datas):
            agendamento = agendamentos_map.get((hora_inicio_str, dia_num))
            celula = {
                'data': data_do_dia,
                'agendamento': agendamento
            }
            linha['celulas'].append(celula)
            
        tabela_horarios.append(linha)


    # --- Cálculo das variáveis de cabeçalho ---
    faixa_datas_semana = {
        'inicio': start_of_week.strftime('%d/%m/%Y'),
        'fim': dias_semana_datas[-1].strftime('%d/%m/%Y')
    }
    
    dias_com_data = []
    for nome, data_obj in zip(dias_semana_nomes, dias_semana_datas):
        dias_com_data.append({
            'nome_dia': nome,
            'data_formatada': data_obj.strftime('%d/%m')
        })
    # --- FIM NOVO: Cálculo das variáveis de cabeçalho ---


    # 6. Manda tudo para o template
    context = {
        'tabela_horarios': tabela_horarios,
        'dias_semana_nomes': dias_semana_nomes,
        'sala': sala_obj,
        'faixa_datas_semana': faixa_datas_semana,
        'dias_com_data': dias_com_data,
        
        # --- VARIÁVEIS DE NAVEGAÇÃO E STATUS ---
        'semana_anterior': semana_anterior.strftime('%Y-%m-%d'),
        'proxima_semana': proxima_semana.strftime('%Y-%m-%d'),
        'status_semana': status_semana, 
        'disable_semana_anterior': disable_semana_anterior, # NOVO
        'disable_proxima_semana': disable_proxima_semana, # NOVO
        # -------------------------------------
    }
    
    return render(request, 'bedesk/detalhe_sala.html', context)

@login_required
def agendar_sala(request):
    # --- PARTE MODIFICADA ---
    # Captura os parâmetros da URL
    hora_predefinida_str = request.GET.get('hora', None)  # ex: "07:00"
    data_predefinida_str = request.GET.get('data', None)  # ex: "2025-11-06"
    sala_nome = request.GET.get('sala', None)

    sala_obj = None
    if sala_nome:
        try:
            sala_obj = Sala.objects.get(nome__iexact=sala_nome)
        except Sala.DoesNotExist:
            sala_obj = None
    
    # --- LÓGICA DE COMBINAÇÃO DE DATA E HORA (GET) ---
    data_predefinida = None
    hora_predefinida_obj = None
    datetime_predefinido = None

    # 1. Converte a string de data (YYYY-MM-DD) para um objeto date
    if data_predefinida_str:
        try:
            data_predefinida = datetime.strptime(data_predefinida_str, '%Y-%m-%d').date()
        except ValueError:
            data_predefinida = None

    # 2. Converte a string de hora (HH:MM) para um objeto time
    if hora_predefinida_str:
        try:
            hora_predefinida_obj = datetime.strptime(hora_predefinida_str, '%H:%M').time()
        except ValueError:
            hora_predefinida_obj = None
            
    # 3. Combina a data e a hora em um único objeto datetime
    if data_predefinida and hora_predefinida_obj:
        datetime_predefinido = datetime.combine(data_predefinida, hora_predefinida_obj)
            
    # Monta o dicionário inicial para o formulário
    initial_data = {
        'horario': hora_predefinida_obj,      # Preenche o campo 'horario'
        'data_inicio': datetime_predefinido,  # Preenche o campo 'data_inicio'
        'sala': sala_obj
    }
    # --- FIM DA PARTE MODIFICADA (GET) ---

    if request.method == 'POST':
        form = AgendarForm(request.POST)
        if form.is_valid():
            nova_reserva = form.save(commit=False)
            
            # --- BLOCO DE SEGURANÇA (POST) ---
            # Garante que o data_inicio (DateTimeField) tenha a hora 
            # correta vinda do campo 'horario', caso o formulário
            # não os tenha combinado automaticamente.
            if nova_reserva.data_inicio and nova_reserva.horario:
                nova_reserva.data_inicio = datetime.combine(
                    nova_reserva.data_inicio.date(),  # Pega a data
                    nova_reserva.horario              # Pega a hora
                )
            # --- FIM DO BLOCO DE SEGURANÇA ---
            
            nova_reserva.usuario = request.user 
            nova_reserva.status = 'PENDENTE'
            nova_reserva.save()
            return redirect('reserva_sucesso')
        
        # Se o form NÃO for válido, ele vai re-renderizar a página 
        # com os erros (o que pode ser o "não está dando certo")
        
    else:
        # Usa os dados iniciais
        form = AgendarForm(initial=initial_data)

    context = {
        'form': form, 
        # (O resto do context é usado apenas para exibir mensagens, se necessário)
        'hora_predefinida': hora_predefinida_str,
        'data_predefinida': data_predefinida,
        'sala_predefinida': sala_nome
    }
    return render(request, 'bedesk/agendar.html', context)
# 2. View de Confirmação de Sucesso
def reserva_sucesso(request):
    # Página simples de confirmação de reserva.
    return render(request, 'bedesk/sucesso.html')

# 3. View para Listar todas as reservas (para o usuário ver suas reservas, por exemplo)
@login_required
@login_required
def lista_reservas(request):
    today = date.today()
    
    # 1. Pega as reservas ativas (futuras e pendentes)
    reservas_ativas = Agendamento.objects.filter(
        usuario=request.user,
        data_inicio__date__gte=today, # Do dia de hoje em diante
        status__in=['APROVADO', 'PENDENTE']
    ).order_by('data_inicio', 'horario')

    # 2. Pega o histórico (passado ou rejeitado)
    reservas_historico = Agendamento.objects.filter(
        usuario=request.user
    ).exclude(
        pk__in=reservas_ativas.values_list('pk', flat=True) # Exclui as que já estão na lista de ativas
    ).order_by('-data_inicio', 'horario')

    context = {
        'reservas_ativas': reservas_ativas,
        'reservas_historico': reservas_historico
    }
    return render(request, 'bedesk/lista_reservas.html', context)

# 
# ADICIONE ESTAS DUAS NOVAS FUNÇÕES NO FINAL DO SEU 'views.py':
# 

@login_required
def cancelar_reserva_usuario(request, agendamento_id):
    """
    Permite ao usuário cancelar uma reserva PENDENTE ou APROVADA (futura).
    Isso muda o status para REJEITADO.
    """
    # Busca a reserva E checa se pertence ao usuário logado
    reserva = get_object_or_404(Agendamento, pk=agendamento_id, usuario=request.user)
    
    # Só pode cancelar se estiver PENDENTE ou APROVADO
    if reserva.status in ['PENDENTE', 'APROVADO']:
        reserva.status = 'REJEITADO'
        reserva.save()
        messages.success(request, "Reserva foi cancelada com sucesso.")
    else:
        messages.warning(request, "Esta reserva não pode ser cancelada.")
        
    return redirect('lista_reserva')




def is_admin_or_staff(user):
    return user.is_staff or user.is_superuser

# Em views.py

# Em views.py

@user_passes_test(is_admin_or_staff)
def gerenciar_reservas(request):
    
    # 1. Reservas de SALAS (como antes)
    reservas_pendentes = Agendamento.objects.filter(
        status='PENDENTE'
    ).order_by('data_inicio')
    
    reservas_aprovadas = Agendamento.objects.filter(
        status='APROVADO'
    ).order_by('-data_inicio', '-horario') 

    # 2. NOVO: Reservas de RECURSOS
    recursos_pendentes = ReservaRecurso.objects.filter(
        status='PENDENTE'
    ).order_by('data_prevista')

    recursos_aprovados = ReservaRecurso.objects.filter(
        status='APROVADO'
    ).order_by('-data_prevista')

    context = {
        # Salas (existente)
        'reservas_pendentes': reservas_pendentes,
        'reservas_aprovadas': reservas_aprovadas,
        
        # Recursos (novo)
        'recursos_pendentes': recursos_pendentes,
        'recursos_aprovados': recursos_aprovados,

        'titulo': 'Gerenciar Reservas e Recursos' 
    }
    return render(request, 'bedesk/gerenciar_reservas.html', context)

@user_passes_test(is_admin_or_staff)
def mudar_status_reserva(request, agendamento_id, novo_status):
    reserva = get_object_or_404(Agendamento, pk=agendamento_id)
      # O novo_status virá como 'APROVADO' ou 'REJEITADO' (em CAPS)
    status_permitidos = ['APROVADO', 'REJEITADO'] # CORREÇÃO: Use 'APROVADO' ou 'REJEITADO' (em CAPS)

    if novo_status not in status_permitidos:
        messages.error(request, 'Status inválido.')
        return redirect('listar_pendentes')

    # Altera o status
    reserva.status = novo_status
    reserva.save()

    # Mensagem de feedback
    if novo_status == 'APROVADO':
          messages.success(request, f'Reserva de {reserva.usuario.username} APROVADA com sucesso!')
    else:
          messages.warning(request, f'Reserva de {reserva.usuario.username} REJEITADA.')

 # Redireciona de volta para a lista (Nome da rota que lista as reservas pendentes)
    return redirect('listar_pendentes')

def logar(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bem-vindo {user.username}!')
            return redirect('inicio')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'registration/login.html')

def log_out(request):
    logout(request)
    return redirect('inicio')

def registrar_usuario(request):
    if request.method == 'POST':
        # Agora usamos o nosso formulário customizado
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            # O método .save() que customizamos no forms.py
            # já cuida de salvar o User E o Profile.
            user = form.save()
            
            messages.success(request, 'Usuário registrado com sucesso! Faça login.')
            return redirect('login')
        # Se o formulário não for válido, ele será renderizado novamente com os erros
    else:
        # Se for um GET, apenas mostra o formulário vazio
        form = CustomUserCreationForm()
        
    return render(request, 'bedesk/registrar_usuario.html', {'form': form})

# Em /bedesk/views.py
# (No topo, verifique se você tem todas estas importações)
from .models import Sala, Agendamento, Recurso, ReservaRecurso
from .forms import AgendarForm, ReservaRecursoForm

# ... (outras importações como messages, redirect, get_object_or_404, etc.)


# ... (suas views existentes: inicio, agendar_sala, lista_reservas, etc.)


# --- ADICIONE ESTAS DUAS NOVAS VIEWS ABAIXO ---


def lista_recursos(request):
    """
    Mostra a página com os "quadrados" de todos os recursos disponíveis
    que o Superuser cadastrou no /admin.
    """
    recursos = Recurso.objects.all()
    context = {
        'recursos': recursos
    }
    return render(request, 'bedesk/lista_recursos.html', context)


@login_required
def reservar_recurso(request, recurso_id):
    """
    Mostra o formulário de reserva para um recurso específico.
    """
    recurso = get_object_or_404(Recurso, pk=recurso_id)
    
    if request.method == 'POST':
        form = ReservaRecursoForm(request.POST)
        if form.is_valid():
            nova_reserva = form.save(commit=False)
            nova_reserva.usuario = request.user
            nova_reserva.recurso = recurso
            nova_reserva.status = 'PENDENTE' # Envia para a fila de aprovação
            nova_reserva.save()
            
            messages.success(request, f"Seu pedido para '{recurso.nome}' foi enviado e está pendente de aprovação.")
            
            # Redireciona para a lista de recursos (ou para "Minhas Reservas", se preferir)
            return redirect('lista_recursos') 
    else:
        form = ReservaRecursoForm()

    context = {
        'form': form,
        'recurso': recurso
    }
    return render(request, 'bedesk/reservar_recurso.html', context)

@user_passes_test(is_admin_or_staff)
def mudar_status_recurso(request, reserva_id, novo_status):
    """
    View para aprovar ou rejeitar uma RESERVA DE RECURSO.
    """
    reserva = get_object_or_404(ReservaRecurso, pk=reserva_id)
    status_permitidos = ['APROVADO', 'REJEITADO']

    if novo_status not in status_permitidos:
        messages.error(request, 'Status inválido.')
        return redirect('listar_pendentes') # Redireciona de volta para /gerenciar

    reserva.status = novo_status
    reserva.save()

    if novo_status == 'APROVADO':
        messages.success(request, f"Reserva de '{reserva.recurso.nome}' para {reserva.usuario.username} APROVADA.")
    else:
        messages.warning(request, f"Reserva de '{reserva.recurso.nome}' para {reserva.usuario.username} REJEITADA.")

    return redirect('listar_pendentes')

# Em /bedesk/views.py

@login_required
def user_profile(request):
    """
    Mostra a página de perfil do usuário.
    Garante que um perfil exista para usuários antigos.
    """
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, 'bedesk/user_profile.html')