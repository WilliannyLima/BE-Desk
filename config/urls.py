# Em /config/urls.py

from django.contrib import admin
from django.urls import path, include # Verifique se 'include' está aqui

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Inclui TODAS as URLs de autenticação do Django (login, logout, reset, etc.)
    # Isso vai ler seus templates na pasta templates/registration/
    path('accounts/', include('django.contrib.auth.urls')), 
    
    # 2. Inclui TODAS as URLs do seu aplicativo (inicio, perfil, gerenciar, etc.)
    path('', include('bedesk.urls')), 
]