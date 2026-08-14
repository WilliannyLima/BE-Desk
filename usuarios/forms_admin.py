from django import forms
from django.contrib.auth import get_user_model

from bedesk.models import Sala

User = get_user_model()


class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['nome', 'capacidade', 'foto']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex.: Ginásio, Sala 12, Quadra'}),
            'capacidade': forms.NumberInput(attrs={'min': 1}),
        }


class PermissionForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=True, label='Usuário')
    is_staff = forms.BooleanField(required=False, label='Pode acessar área administrativa (is_staff)')
    is_superuser = forms.BooleanField(required=False, label='Superusuário (is_superuser)')
