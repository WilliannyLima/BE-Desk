from django.shortcuts import render
from .forms import AgendarForm
# Create your views here.
def index(request):
    return render(request, 'index.html')

def inicio(request):
    return render(request, 'inicio.html')

def ginasio(request):
    return render(request, 'ginasio.html')

def piscina(request):
    return render(request, 'piscina.html')

def salas(request):
    return render(request, 'salas.html')

def agendar_view(request):
    if request.method == 'POST':
        form = AgendarForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'agendar_success.html')
    else:
        form = AgendarForm()
    return render(request, 'bedesk/index.html', {'form': form}) #render(request, 'agendar.html', {'form': form})