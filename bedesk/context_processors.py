# Em /bedesk/context_processors.py

from .models import Agendamento

def notificacoes_pendentes(request):
    """
    Verifica se existem reservas pendentes e disponibiliza a contagem
    para todos os templates.
    """
    
    # Inicia a contagem como 0
    pendentes_count = 0
    
    # Só faz a consulta no banco se o usuário for staff (otimização)
    if request.user.is_authenticated and request.user.is_staff:
        pendentes_count = Agendamento.objects.filter(status='PENDENTE').count()
    
    # Retorna um dicionário que será adicionado ao contexto do template
    return {
        'pendentes_count': pendentes_count
    }