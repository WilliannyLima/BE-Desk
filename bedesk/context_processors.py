# Em /bedesk/context_processors.py

# Importe os dois modelos
from .models import Agendamento, ReservaRecurso 

def notificacoes_pendentes(request):
    """
    Verifica se existem reservas PENDENTES de Salas E Recursos
    e disponibiliza a contagem total para todos os templates.
    """
    
    total_pendentes = 0
    
    if request.user.is_authenticated and request.user.is_staff:
        # 1. Conta as salas pendentes
        salas_pendentes_count = Agendamento.objects.filter(status='PENDENTE').count()
        
        # 2. Conta os recursos pendentes
        recursos_pendentes_count = ReservaRecurso.objects.filter(status='PENDENTE').count()
        
        # 3. Soma os dois
        total_pendentes = salas_pendentes_count + recursos_pendentes_count
    
    return {
        'pendentes_count': total_pendentes
    }