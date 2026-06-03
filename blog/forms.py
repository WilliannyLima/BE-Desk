from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'slug', 'summary', 'content', 'cover', 'is_published', 'published_at']
        widgets = {
            'published_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'title': forms.TextInput(attrs={'placeholder': 'Digite o título da publicação'}),
            'slug': forms.TextInput(attrs={'placeholder': 'ex: meu-artigo-legal'}),
            'summary': forms.Textarea(attrs={'placeholder': 'Digite um resumo curto (visível na lista)'}),
            'content': forms.Textarea(attrs={'placeholder': 'Escreva o conteúdo da publicação aqui...', 'rows': 12}),
        }
        labels = {
            'title': 'Título',
            'slug': 'Slug (URL)',
            'summary': 'Resumo',
            'content': 'Conteúdo',
            'cover': 'Imagem de capa',
            'is_published': 'Publicado',
            'published_at': 'Data de publicação',
        }
        help_texts = {
            'slug': 'Endereço amigável usado na URL (ex: "meu-artigo").',
            'published_at': 'Data e hora em que a publicação entra no ar.',
        }
