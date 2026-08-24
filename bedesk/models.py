from django.db import models
from django.contrib.auth.models import User # Use 'auth.User' ou importe User diretamente

class Sala(models.Model):
    # Um modelo simples para a sala. Você pode expandir este modelo
    nome = models.CharField(max_length=100)
    capacidade = models.IntegerField(default=1)
    foto = models.ImageField(
        upload_to='salas/',
        blank=True,
        null=True,
        verbose_name="Foto do local",
        help_text="Imagem exibida no card do local na listagem.",
    )

    def __str__(self):
        return self.nome

class Agendamento(models.Model):

    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('APROVADO', 'Aprovado'),
        ('REJEITADO', 'Rejeitado'),
    ]

    nome = models.CharField(max_length=100)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    motivo = models.TextField()
    horario = models.TimeField()

    data_inicio = models.DateTimeField(null=True, blank=True)
    data_fim = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDENTE'
    )

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Agendamentos"
        indexes = [models.Index(fields=['status'])]

    def __str__(self):
        data_str = self.data_inicio.strftime('%d/%m/%Y') if self.data_inicio else 'Data não definida'
        return f"{self.nome} - {self.sala.nome} em {data_str}"

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

# 1. O Modelo do Perfil
class Profile(models.Model):
    # Papéis do sistema. Derivados das flags do Django para evitar duas
    # fontes de verdade: professor = superuser, bolsista = staff.
    PROFESSOR = 'PROFESSOR'
    BOLSISTA = 'BOLSISTA'
    ALUNO = 'ALUNO'

    PAPEL_LABELS = {
        PROFESSOR: 'Professor',
        BOLSISTA: 'Aluno bolsista',
        ALUNO: 'Aluno',
    }

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=50, blank=True, verbose_name="Matrícula")

    @property
    def papel(self):
        if self.user.is_superuser:
            return self.PROFESSOR
        if self.user.is_staff:
            return self.BOLSISTA
        return self.ALUNO

    @property
    def papel_label(self):
        return self.PAPEL_LABELS[self.papel]

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
