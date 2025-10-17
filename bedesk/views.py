from django.shortcuts import render
from .forms import AgendarForm
# Create your views here.
def index(request):
    if request.method == 'POST':
        form = AgendarForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'agendar_successo.html')
 # Página de sucesso após agendamento
    else:
        form = AgendarForm()
    context = {'form': form}
    return render(request, 'index.html', context)
    

def inicio(request):
    return render(request, 'inicio.html')

def ginasio(request):
    return render(request, 'ginasio.html')

def piscina(request):
    return render(request, 'piscina.html')

def salas(request):
    return render(request, 'salas.html')

#render(request, 'agendar.html', {'form': form})