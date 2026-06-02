from django import forms
from django.contrib.auth import get_user_model

from bedesk.models import Sala, Recurso

User = get_user_model()


class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['nome', 'capacidade']


class RecursoForm(forms.ModelForm):
    class Meta:
        model = Recurso
        fields = ['nome', 'descricao']


class PermissionForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=True, label='Usuário')
    is_staff = forms.BooleanField(required=False, label='Pode acessar área administrativa (is_staff)')
    is_superuser = forms.BooleanField(required=False, label='Superusuário (is_superuser)')
