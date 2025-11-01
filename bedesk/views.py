from django.shortcuts import render, redirect, get_object_or_404 
from .forms import AgendarForm 
from .models import Agendamento, Sala
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import logout, authenticate, login
from datetime import datetime, timedelta
from django.contrib.auth.forms import UserCreationForm
 
    
    
def inicio(request):
    horarios = []
    inicio = datetime.strptime("07:00", "%H:%M")
    fim = datetime.strptime("18:00", "%H:%M")
    delta = timedelta(minutes=45)

    while inicio <= fim:
        horarios.append(inicio.strftime("%H:%M"))
        inicio += delta

    return render(request, 'bedesk/inicio.html', {'horarios': horarios})
    # CORREÇÃO: Removido o espaço antes do 'bedesk/inicio.html'
    


# 1. View para Agendar a Sala (Criação)
def agendar_sala(request):
    hora_predefinida = request.GET.get('hora', None)
    sala_nome = request.GET.get('sala', None)
    
    sala_obj = None
    if sala_nome:
        try:
            sala_obj = Sala.objects.get(nome__iexact=sala_nome)
        except Sala.DoesNotExist:
            sala_obj = None
            
    
    if request.method == 'POST':
        form = AgendarForm(request.POST)
        if form.is_valid():
            nova_reserva = form.save(commit=False)
            nova_reserva.usuario = request.user # Define o usuário logado
            nova_reserva.status = 'PENDENTE' # CORREÇÃO: Use 'PENDENTE' (em CAPS) conforme o models.py
            nova_reserva.save()
            # CORREÇÃO: Use o NOME DA URL (que deve ser 'reserva_sucesso' no seu urls.py)
            return redirect('reserva_sucesso') 
    else:
        form = AgendarForm(initial={'horario': hora_predefinida,'sala': sala_obj})
    context = {'form': form, 'hora_predefinida': hora_predefinida,'sala_predefinida': sala_nome}
    # CORREÇÃO: Removido o espaço antes do 'bedesk/agendar.html'
    return render(request, 'bedesk/agendar.html', context)

# 2. View de Confirmação de Sucesso
def reserva_sucesso(request):
    # Página simples de confirmação de reserva.
    return render(request, 'bedesk/sucesso.html')

# 3. View para Listar todas as reservas (para o usuário ver suas reservas, por exemplo)
def lista_reservas(request):
    # ATENÇÃO: Se seu campo de data for 'data_inicio' e não 'data', ajuste aqui
    reservas = Agendamento.objects.all().order_by('-data_inicio', '-horario') 
    # Assumindo que você está consolidando no 'bedesk':
    context = {'reservas': reservas}
    return render(request, 'bedesk/lista_reservas.html', context) 

def is_admin_or_staff(user):
    return user.is_staff

@user_passes_test(is_admin_or_staff)
def gerenciar_reservas(request):
    # CORREÇÃO: Use 'PENDENTE' (em CAPS) conforme o models.py
    reservas = Agendamento.objects.filter(status='PENDENTE').order_by('data_inicio')
    context = {'reservas': reservas,
               'titulo':'Reservas Pendentes de Aprovação'
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


# 4. View para Editar uma Reserva (Corrigida)
def editar_reserva(request, id):
    reserva = get_object_or_404(Agendamento, id=id)
    salas = Sala.objects.all() # Assumindo que você precisa de todas as salas

    if request.method == 'POST':
        # Você deve usar um formulário (AgendarForm) aqui para validação!
        # Exemplo de como salvar dados brutos, mas recomenda-se usar o Form:
        reserva.sala_id = request.POST.get('sala')
        reserva.data = request.POST.get('data') # Cuidado com o nome do campo de data
        reserva.hora = request.POST.get('hora') # Cuidado com o nome do campo de hora
        reserva.save()
        messages.success(request, 'Reserva atualizada com sucesso!')
        # CORREÇÃO: Usando 'lista_reserva'
        return redirect('lista_reserva') 

    # O template deve estar em 'bedesk/editar_reserva.html' ou 'editar_reserva.html'
    return render(request, 'editar_reserva.html', {'reserva': reserva, 'salas': salas})

# 5. View para Excluir uma Reserva (Corrigida)
def excluir_reserva(request, id):
    reserva = get_object_or_404(Agendamento, id=id)
    reserva.delete()
    messages.success(request, 'Reserva excluída com sucesso!')
    # CORREÇÃO: Usando 'lista_reserva'
    return redirect('lista_reserva')

def log_out(request):
    logout(request)
    return redirect('inicio')

def registrar_usuario(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário registrado com sucesso! Faça login.')
            return redirect('logar')
    else:
        form = UserCreationForm()
    return render(request, 'bedesk/registrar_usuario.html', {'form': form})
