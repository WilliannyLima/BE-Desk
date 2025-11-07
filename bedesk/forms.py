# Em bedesk/forms.py

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Agendamento, Recurso, ReservaRecurso, Profile # Mantenha seus imports
import datetime # Mantenha seus imports

#
# MANTENHA SEUS FORMULÁRIOS 'AgendarForm' e 'ReservaRecursoForm' AQUI
#

class AgendarForm(forms.ModelForm):
    # (O seu código do AgendarForm está correto, mantenha ele aqui)
    class Meta:
        model = Agendamento
        fields = ['nome', 'sala', 'motivo', 'horario', 'data_inicio']
        widgets = {
            'motivo': forms.Textarea(attrs={'rows': 4}),
            'horario': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'data_inicio': forms.HiddenInput(),
        }
    
    def clean(self):
        # (O seu método clean() está correto, mantenha ele aqui)
        cleaned_data = super().clean()
        sala = cleaned_data.get('sala')
        horario = cleaned_data.get('horario')
        data_inicio = cleaned_data.get('data_inicio')
        HORARIO_ABERTURA = datetime.time(7, 0)
        HORARIO_FECHAMENTO = datetime.time(18, 0) 
        if horario and (horario < HORARIO_ABERTURA or horario > HORARIO_FECHAMENTO):
             self.add_error('horario', f"O horário deve estar entre {HORARIO_ABERTURA.strftime('%H:%M')} e {HORARIO_FECHAMENTO.strftime('%H:%M')}.")
             return cleaned_data 
        if sala and data_inicio and horario:
            data_do_agendamento = data_inicio.date() 
            conflitos = Agendamento.objects.filter(
                sala=sala, 
                data_inicio__date=data_do_agendamento,
                horario=horario,
                status__in=['PENDENTE', 'APROVADO']
            )
            if self.instance and self.instance.pk:
                conflitos = conflitos.exclude(pk=self.instance.pk)
            if conflitos.exists():
                self.add_error(
                    None,
                    f"A sala {sala.nome} já tem uma reserva (Pendente ou Aprovada) para as {horario.strftime('%H:%M')} de {data_do_agendamento.strftime('%d/%m/%Y')}."
                )
        return cleaned_data

class ReservaRecursoForm(forms.ModelForm):
    # (O seu código do ReservaRecursoForm está correto, mantenha ele aqui)
    class Meta:
        model = ReservaRecurso
        fields = ['data_prevista', 'motivo_uso', 'local_uso']
        widgets = {
            'data_prevista': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'motivo_uso': forms.Textarea(
                attrs={'rows': 4, 'class': 'form-control'}
            ),
            'local_uso': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
        }

# ===================================================================
# SUBSTITUA OU ADICIONE ESTA CLASSE 'CustomUserCreationForm'
# ===================================================================
class CustomUserCreationForm(UserCreationForm):
    """
    Formulário de criação de usuário que pede Email e Nome Completo.
    (O seu template 'widget_tweaks' cuida do estilo 'form-control')
    """
    
    # 1. Definição dos campos
    email = forms.EmailField(
        required=True, 
        label="Email"
    )
    nome_completo = forms.CharField(
        max_length=150, 
        required=True, 
        label="Nome Completo"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'nome_completo',) # Campos que o usuário VÊ
        # (Não precisamos de 'widgets' porque seu template cuida disso)

    # 2. Validação
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists() or \
           User.objects.filter(username=email).exists():
            raise forms.ValidationError("Este email já está em uso. Tente outro.")
        return email

    # 3. Lógica de Salvar
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email'] 
        user.email = self.cleaned_data['email']

        full_name = self.cleaned_data.get('nome_completo')
        if full_name:
            parts = full_name.split(' ', 1) 
            user.first_name = parts[0]
            if len(parts) > 1:
                user.last_name = parts[1]
            else:
                user.last_name = ''
        
        if commit:
            user.save()
            
        return user