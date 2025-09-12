from django.shortcuts import render
from django.http import HttpResponse

def recursos(request):
    return render(request, "ver_recursos.html")

def login(request):
    return render(request, 'login.html')

def inicio(request):
    return render(request, 'inicio.html')

# Create your views here.
