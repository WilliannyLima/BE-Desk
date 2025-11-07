from django.shortcuts import render, redirect, get_object_or_404
from .forms import AgendarForm
from .models import Sala, Agendamento
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth import logout, authenticate, login
from datetime import datetime, timedelta
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime, timedelta, date

@login_required
def inicio(request):
    # --- 1. Definição da Estrutura Fixa de Horários (Conforme sua imagem) ---
    
    # Esta lista define a estrutura exata da sua tabela
    horarios_estrutura = [
        {'tipo': 'separador', 'nome': 'Manhã'},
        {'tipo': 'hora', 'inicio': '07:00', 'fim': '07:45'},
        {'tipo': 'hora', 'inicio': '07:45', 'fim': '08:30'},
        {'tipo': 'intervalo', 'inicio': '08:30', 'fim': '08:50', 'nome': 'Intervalo (20 min)'}, # Intervalo de 20 min
        {'tipo': 'hora', 'inicio': '08:50', 'fim': '09:35'},
        {'tipo': 'hora', 'inicio': '09:35', 'fim': '10:20'},
        {'tipo': 'intervalo', 'inicio': '10:20', 'fim': '10:30', 'nome': 'Intervalo (10 min)'}, # Intervalo de 10 min
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

    # --- 2. Buscar Dados da Semana Atual ---
    
    # IMPORTANTE: Confirme que o nome da sala é 'Ginásio' no seu BD.
    try:
        sala_ginasio = Sala.objects.get(nome='Ginásio') 
    except Sala.DoesNotExist:
        messages.error(request, "A sala 'Ginásio' não foi encontrada no sistema.")
        return render(request, 'bedesk/inicio.html', {'tabela_horarios': [], 'dias_semana_nomes': dias_semana_nomes})

    today = date.today()
    start_of_week = today - timedelta(days=today.weekday()) # Segunda-feira
    
    # Lista das 5 datas da semana (objetos date)
    dias_semana_datas = [start_of_week + timedelta(days=i) for i in range(5)]

    # Busca agendamentos APROVADOS para esta sala, nesta semana
    agendamentos = Agendamento.objects.filter(
        sala=sala_ginasio,
        status='APROVADO',
        data_inicio__date__range=[start_of_week, dias_semana_datas[-1]]
    ).select_related('usuario')

    # --- 3. Mapear Agendamentos para a Grade ---
    agendamentos_map = {}
    for ag in agendamentos:
        hora_str = ag.horario.strftime("%H:%M")
        dia_weekday = ag.data_inicio.weekday() # 0=Seg, 1=Ter...
        agendamentos_map[(hora_str, dia_weekday)] = ag

    # --- 4. Construir a Tabela para o Template ---
    tabela_horarios = []
    for item in horarios_estrutura:
        
        # Se for um separador ('Manhã', 'Tarde') ou intervalo
        if item['tipo'] != 'hora':
            tabela_horarios.append(item)
            continue
        
        # Se for um horário normal
        hora_inicio_str = item['inicio']
        linha = {
            'tipo': 'hora',
            'horario_str': f"{item['inicio']} às {item['fim']}",
            'hora_para_link': hora_inicio_str, # Apenas a hora de início para o link
            'celulas': [] # Lista para as 5 células (Seg-Sex)
        }
        
        for dia_num, data_do_dia in enumerate(dias_semana_datas):
            # Pega o agendamento no map, ou None se não existir
            agendamento = agendamentos_map.get((hora_inicio_str, dia_num))
            
            celula = {
                'data': data_do_dia,
                'agendamento': agendamento
            }
            linha['celulas'].append(celula)
            
        tabela_horarios.append(linha)

    # --- 5. Enviar para o Template ---
    context = {
        'tabela_horarios': tabela_horarios,
        'dias_semana_nomes': dias_semana_nomes,
        'sala_ginasio_nome': sala_ginasio.nome, # Para usar no link do botão
    }
    return render(request, 'bedesk/inicio.html', context)


# 1. View para Agendar a Sala (Criação)
# Em views.py

# (Verifique se 'from datetime import datetime, timedelta, date' está no topo)

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


@login_required
def excluir_reserva_usuario(request, agendamento_id):
    """
    Permite ao usuário EXCLUIR uma reserva do seu histórico.
    Isso SÓ funciona para reservas REJEITADAS ou PASSADAS.
    """
    # Busca a reserva E checa se pertence ao usuário logado
    reserva = get_object_or_404(Agendamento, pk=agendamento_id, usuario=request.user)
    
    # Regra: Só pode excluir se NÃO estiver PENDENTE ou APROVADA (futura)
    if reserva.status == 'REJEITADO' or (reserva.data_inicio.date() < date.today()):
        reserva_id = reserva.id
        reserva.delete()
        messages.success(request, f"Reserva (ID: {reserva_id}) foi excluída do seu histórico.")
    else:
        messages.warning(request, "Você não pode excluir uma reserva ativa. Use 'Cancelar' primeiro.")

    return redirect('lista_reserva') 

def is_admin_or_staff(user):
    return user.is_staff or user.is_superuser

# Em views.py

# Em views.py

@user_passes_test(is_admin_or_staff)
def gerenciar_reservas(request):
    
    # 1. Buscar as reservas PENDENTES (igual antes)
    reservas_pendentes = Agendamento.objects.filter(
        status='PENDENTE'
    ).order_by('data_inicio')
    
    # 2. CORREÇÃO: Buscar TODAS as reservas APROVADAS
    
    # Removemos o filtro 'data_inicio__date__gte=date.today()'
    # E ordenamos da mais recente/futura para a mais antiga ('-data_inicio')
    
    reservas_aprovadas = Agendamento.objects.filter(
        status='APROVADO'
    ).order_by('-data_inicio', '-horario') 

    context = {
        'reservas_pendentes': reservas_pendentes,
        'reservas_aprovadas': reservas_aprovadas, # Lista corrigida
        'titulo': 'Gerenciar Reservas' 
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
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False  # Define como False para usuários comuns
            user.is_superuser = False  # Define como False para usuários comuns
            form.save()
            
            messages.success(request, 'Usuário registrado com sucesso! Faça login.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'bedesk/registrar_usuario.html', {'form': form})
