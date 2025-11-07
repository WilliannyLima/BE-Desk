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

class Recurso(models.Model):
    """
    O item que pode ser reservado (ex: Bola de Futsal, Corda).
    O Superuser vai adicionar/editar estes itens pela tela /admin.
    """
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True, help_text="Descrição, regras de uso, etc.")
    # Adicionaremos um campo de imagem no futuro, para os "quadrados"
    
    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Recurso"
        verbose_name_plural = "Recursos"


class ReservaRecurso(models.Model):
    """
    O pedido de reserva de um recurso, que irá para a fila de aprovação.
    """
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('APROVADO', 'Aprovado'),
        ('REJEITADO', 'Rejeitado'),
    ]
    
    # O que está sendo reservado
    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE)
    
    # Quem está pedindo
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Status da aprovação (igual ao Agendamento)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDENTE'
    )
    
    # Respostas do novo formulário
    data_prevista = models.DateTimeField(verbose_name="Quando você precisa?")
    motivo_uso = models.TextField(verbose_name="Para que o recurso será usado?")
    local_uso = models.CharField(max_length=200, verbose_name="Onde você irá utilizá-lo?")
    
    # Data de criação do pedido
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.recurso.nome} ({self.status})"
        
    class Meta:
        # Ordena os pedidos mais novos primeiro
        ordering = ['-criado_em']
        verbose_name = "Reserva de Recurso"
        verbose_name_plural = "Reservas de Recursos"

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

# 1. O Modelo do Perfil
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=50, blank=True, verbose_name="Matrícula")

    def __str__(self):
        return f'{self.user.username} Profile'

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"

# 2. Sinais (Signals) para criar o perfil automaticamente
# Esta função será executada SEMPRE que um usuário for criado
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Esta função salva o perfil
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    # Tenta buscar o perfil, se não existir, cria um (para usuários antigos)
    profile, created = Profile.objects.get_or_create(user=instance)
    profile.save()
