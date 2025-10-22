from django.contrib import admin
from django.urls import path
from . import views
# Em bedesk/urls.py
urlpatterns = [
    path('agendar/', views.agendar_sala, name='agendar_sala'),
    path('agendamento/sucesso/', views.reserva_sucesso, name='reserva_sucesso'),
    # ...
]