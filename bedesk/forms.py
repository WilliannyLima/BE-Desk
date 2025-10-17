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
def clean_horario(self):
    horario = self.cleaned_data['horario']
    if horario < datetime.time(7, 0) or horario > datetime.time(18, 0):
        raise forms.ValidationError("O horário deve estar entre 07:00 e 18:00.")
    return horario 