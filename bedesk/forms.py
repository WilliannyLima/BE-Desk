# Em forms.py

from django import forms
from .models import Agendamento, Recurso, ReservaRecurso
import datetime

class AgendarForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        
        # --- PASSO 1: CORREÇÃO PRINCIPAL ---
        # Adicionamos 'data_inicio' à lista de campos.
        fields = ['nome', 'sala', 'motivo', 'horario', 'data_inicio']
        
        # --- PASSO 2: CONSOLIDAR WIDGETS ---
        widgets = {
            'motivo': forms.Textarea(attrs={'rows': 4}),
            'horario': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            
            # Nós escondemos 'data_inicio' porque a view já o preenche.
            # O template (agendar.html) já o esconde, mas isso é uma 
            # garantia extra e define o widget correto.
            'data_inicio': forms.HiddenInput(),
        }

    # --- PASSO 3: CORRIGIR O MÉTODO CLEAN ---
    def clean(self):
        cleaned_data = super().clean()
        
        # Pegar os dados corretos que agora estão sendo processados
        sala = cleaned_data.get('sala')
        horario = cleaned_data.get('horario')
        data_inicio = cleaned_data.get('data_inicio') # O DateTimeField

        # --- Validação 1: Expediente (das 07:00 às 18:00) ---
        HORARIO_ABERTURA = datetime.time(7, 0)
        HORARIO_FECHAMENTO = datetime.time(18, 0) 

        if horario and (horario < HORARIO_ABERTURA or horario > HORARIO_FECHAMENTO):
             self.add_error('horario', f"O horário deve estar entre {HORARIO_ABERTURA.strftime('%H:%M')} e {HORARIO_FECHAMENTO.strftime('%H:%M')}.")
             # Parar a validação aqui se o horário for inválido
             return cleaned_data 

        # --- Validação 2: Disponibilidade (Verificação de Conflito) ---
        
        # Verifica se todos os dados necessários existem antes de checar
        if sala and data_inicio and horario:
            
            # 'data_inicio' é um objeto datetime (data+hora).
            # Nós pegamos apenas a .date() dele para a busca.
            data_do_agendamento = data_inicio.date() 
            
            # Procura por agendamentos APROVADOS ou PENDENTES
            conflitos = Agendamento.objects.filter(
                sala=sala, 
                data_inicio__date=data_do_agendamento, # Compara só a data
                horario=horario,                      # Compara a hora
                status__in=['PENDENTE', 'APROVADO']   # Ignora rejeitados
            )

            # Se esta é uma *edição* (self.instance.pk existe), 
            # exclui a si mesmo da verificação de conflito.
            if self.instance and self.instance.pk:
                conflitos = conflitos.exclude(pk=self.instance.pk)

            # Se encontrou algum conflito...
            if conflitos.exists():
                self.add_error(
                    None, # Adiciona o erro ao topo do formulário
                    f"A sala {sala.nome} já tem uma reserva (Pendente ou Aprovada) para as {horario.strftime('%H:%M')} de {data_do_agendamento.strftime('%d/%m/%Y')}."
                )
        
        return cleaned_data

class ReservaRecursoForm(forms.ModelForm):
    class Meta:
        model = ReservaRecurso
        
        # Estes são os campos que o usuário irá preencher
        # (O 'recurso', 'usuario' e 'status' serão definidos na view)
        fields = ['data_prevista', 'motivo_uso', 'local_uso']
        
        # Adiciona widgets para os campos (para o Bootstrap)
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
# O 'clean_horario' e o 'widgets' que estavam aqui embaixo
# foram removidos pois já estão incluídos na classe acima.