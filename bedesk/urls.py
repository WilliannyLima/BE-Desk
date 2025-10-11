# CÓDIGO CORRETO
from django.urls import path
from django.contrib import admin
from bedesk import views  # Importa o módulo views

urlpatterns = [
    # A linha do admin provavelmente deveria estar no urls.py do projeto (config), não no app.
    path('admin/', admin.site.urls), 

    path('', views.index, name='index'),           # CORRIGIDO
    path('inicio/', views.inicio, name='inicio'),
       # CORRIGIDO
]