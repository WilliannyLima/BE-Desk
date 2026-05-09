from django import forms

from bedesk.models import ReservaRecurso


class ReservaRecursoForm(forms.ModelForm):
    class Meta:
        model = ReservaRecurso
        fields = ["data_prevista", "motivo_uso", "local_uso"]
        widgets = {
            "data_prevista": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "motivo_uso": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "local_uso": forms.TextInput(attrs={"class": "form-control"}),
        }
