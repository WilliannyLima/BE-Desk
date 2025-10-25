# reservas/views.py (Corrigido)

from django.shortcuts import render, redirect, get_object_or_404 
from .forms import AgendarForm 
from .models import Agendamento
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test


def inicio(request):
    # CORREÇÃO: Removido o espaço antes do 'bedesk/inicio.html'
    return render(request, 'bedesk/inicio.html')


# 1. View para Agendar a Sala (Criação)
def agendar_sala(request):
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
        form = AgendarForm()
    context = {'form': form}
    # CORREÇÃO: Removido o espaço antes do 'bedesk/agendar.html'
    return render(request, 'bedesk/agendar.html', context)

# 2. View de Confirmação de Sucesso
def reserva_sucesso(request):
    # Página simples de confirmação de reserva.
    return render(request, 'bedesk/sucesso.html')

# 3. View para Listar todas as reservas (para o usuário ver suas reservas, por exemplo)
def listar_reservas(request):
    # ATENÇÃO: Se seu campo de data for 'data_inicio' e não 'data', ajuste aqui
    reservas = Agendamento.objects.all().order_by('-data_inicio', '-horario') 
    # CORREÇÃO: O template deve estar em 'bedesk/' ou no app 'reservas/'.
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
    # Esta view não é necessária se você estiver usando 'django.contrib.auth.urls'
    # Mas se for customizada:
    return render(request, 'registration/login.html')