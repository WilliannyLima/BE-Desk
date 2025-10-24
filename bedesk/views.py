# reservas/views.py

from django.shortcuts import render, redirect # Importa render e redirect para redirecionamento
from .forms import AgendarForm             # Importa o formulário que você criou

# 1. View para Agendar a Sala (Criação)
def agendar_sala(request):
    """
    Exibe o formulário de agendamento e processa a submissão.
    """
    if request.method == 'POST':
        # Cria uma instância do formulário com os dados enviados (POST)
        form = AgendarForm(request.POST) 
        
        # O método is_valid() chama o clean() do formulário, 
        # que verifica a disponibilidade e o horário de funcionamento.
        if form.is_valid():
            form.save() # Salva a reserva no banco de dados
            return redirect('reserva_sucesso') # Redireciona para a página de sucesso
    else:
        # Se não for POST (primeira vez que a página é carregada), 
        # cria um formulário vazio
        form = AgendarForm()
        
    context = {'form': form}

    return render(request, 'index.html', context)

    dias_semana = [d[0] for d in Agendamento.DIA_SEMANA]

    aprovados = Agendamento.objects.filter(status='Aprovado')
    
    dados_Agendamento = {}
    for dia in dias_semana: 
        dados_Agendamento[dia] = {}

    for booking in aprovados:
        dia = agendamento.dia
        dados_Agendamento[dia]

    # Renderiza o template com o formulário
    return render(request, 'agendar.html', context)

# 2. View de Confirmação de Sucesso
def reserva_sucesso(request):
    
#    Página simples de confirmação de reserva.
    
    return render(request, 'sucesso.html')






    def listar_reservas(request):

 #   Lista todas as reservas existentes.
   
     reservas = Agendamento.objects.all().order_by('-data', '-horario')
     context = {'reservas': reservas}
     return render(request, 'reservas/lista_reservas.html', context)