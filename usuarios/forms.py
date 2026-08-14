from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    nome_completo = forms.CharField(
        max_length=150,
        required=True,
        label="Nome Completo",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "nome_completo")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            raise forms.ValidationError("Este email já está em uso. Tente outro.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]

        full_name = self.cleaned_data.get("nome_completo")
        if full_name:
            parts = full_name.split(" ", 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ""

        if commit:
            user.save()

        return user
