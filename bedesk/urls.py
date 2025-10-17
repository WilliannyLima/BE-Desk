# CÓDIGO CORRETO
from django.urls import path
from django.contrib import admin
from bedesk import views  # Importa o módulo views

urlpatterns = [
    # A linha do admin provavelmente deveria estar no urls.py do projeto (config), não no app.
    path('admin/', admin.site.urls), 

    path('', views.index, name='index'),           # CORRIGIDO
    path('inicio/', views.inicio, name='inicio'),
    path('ginasio/', views.ginasio, name='ginasio'),
    path('piscina/', views.piscina, name='piscina'),
    path('salas/', views.salas, name='salas'),


    path('agendar/', views.agendar_view, name='agendar'),  # Adiciona a URL para a view agendar_view
    path('agendamento/successo/', views.agendar_view, name='agendar_successo'),  # Página de sucesso após agendamento
]