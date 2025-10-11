from django.shortcuts import render

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