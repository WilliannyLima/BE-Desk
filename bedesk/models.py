from django.db import models



class Agendamento(models.Model):
    nome = models.CharField(max_length=100)
    motivo = models.TextField()
    horario = models.TimeField()

    def __str__(self):
        return f"{self.nome} - {self.horario}"
    

