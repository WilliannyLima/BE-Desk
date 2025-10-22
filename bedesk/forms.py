from django import forms
from .models import Agendamento
import datetime

class AgendarForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['nome', 'motivo', 'horario']
        widgets = {
            'horario': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        sala = cleaned_data.get('sala')
        data = cleaned_data.get('data')
        horario = cleaned_data.get('horario')

        # === Validação 1: Expediente (ajuste conforme o horário das salas) ===
        # Exemplo: As salas só estão abertas das 07:00 às 22:00
        HORARIO_ABERTURA = datetime.time(7, 0)
        HORARIO_FECHAMENTO = datetime.time(22, 0)

        if horario and (horario < HORARIO_ABERTURA or horario > HORARIO_FECHAMENTO):
             self.add_error('horario', f"O horário deve estar entre {HORARIO_ABERTURA.strftime('%H:%M')} e {HORARIO_FECHAMENTO.strftime('%H:%M')}.")
             # Retornar early se o horário for inválido
             return cleaned_data
        
        # === Validação 2: Disponibilidade (a regra de ouro da reserva) ===
        if sala and data and horario:
            # 💡 Verifica se já existe uma reserva para ESTA SALA, NESTA DATA, NESTE HORÁRIO
            if Agendamento.objects.filter(sala=sala, data=data, horario=horario).exists():
                self.add_error(
                    'horario',
                    f"A sala {sala.nome} já está reservada para as {horario.strftime('%H:%M')} de {data.strftime('%d/%m/%Y')}."
                )
        
        return cleaned_data