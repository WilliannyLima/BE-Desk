from django.db import models
from django.contrib.auth.models import User # Use 'auth.User' ou importe User diretamente

class Sala(models.Model):
    # Um modelo simples para a sala. Você pode expandir este modelo
    nome = models.CharField(max_length=100)
    capacidade = models.IntegerField(default=1) 

    def __str__(self):
        return self.nome

class Agendamento(models.Model):
    # 1. Escolhas de Status (Definidas no topo da classe)
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'), # O valor que vai para o banco (melhor em CAPS)
        ('APROVADO', 'Aprovado'), # O valor que o usuário vê (após a vírgula)
        ('REJEITADO', 'Rejeitado'),
    ]

    # Campos de Dados
    nome = models.CharField(max_length=100) # Nome do Agendamento (ex: Reunião de Marketing)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    motivo = models.TextField()
    horario = models.TimeField()
    
    # Datas (Null e Blank True porque o agendamento pode ser feito antes da definição exata)
    data_inicio = models.DateTimeField(null=True, blank=True)
    data_fim = models.DateTimeField(null=True, blank=True) 
    
    # Campo de Status (Corrigido: sem vírgula final e usando as choices)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDENTE' # Valor padrão para novas reservas
    ) 
    
    # Chaves Estrangeiras
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE) 
    # Usando 'User' diretamente após a importação. 
    # Caso use 'auth.User', a importação de User não é necessária.
    usuario = models.ForeignKey(User, on_delete=models.CASCADE) 

    class Meta:
        # Define o nome da tabela no plural de forma mais legível
        verbose_name_plural = "Agendamentos" 
        # Adiciona um índice para otimizar a busca por status
        indexes = [
            models.Index(fields=['status']),
        ]

    def __str__(self):
        # Garante que a data_inicio não é None antes de formatar, para evitar erros
        data_str = self.data_inicio.strftime('%d/%m/%Y') if self.data_inicio else 'Data não definida'
        return f"{self.nome} - {self.sala.nome} em {data_str}"



