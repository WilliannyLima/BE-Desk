from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # Keep form minimal: slug, published state and date are managed by views/model
        fields = ['title', 'summary', 'content', 'cover']
        widgets = {
            'published_at': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'title': forms.TextInput(attrs={
                'placeholder': 'Digite o título da publicação',
                'autocomplete': 'off',
            }),
            'summary': forms.Textarea(attrs={
                'placeholder': 'Digite um resumo curto (visível na lista)',
                'rows': 3,
            }),
            'content': forms.Textarea(attrs={
                'placeholder': 'Escreva o conteúdo da publicação aqui...',
                'rows': 12,
            }),
        }
        labels = {
            'title': 'Título',
            'summary': 'Resumo',
            'content': 'Conteúdo',
            'cover': 'Imagem de capa',
            # publication status and date are set by the action buttons
        }
        help_texts = {
            # kept intentionally empty for simplified form
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # No extra initialization required; published fields handled by views
