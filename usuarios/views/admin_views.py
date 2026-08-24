from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from bedesk.models import Sala, Profile, Agendamento
from usuarios.forms_admin import SalaForm, PermissionForm
from blog.models import Post
from blog.forms import PostForm
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

User = get_user_model()


def staff_required(view_func):
    return user_passes_test(lambda u: u.is_active and u.is_staff)(view_func)


def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_active and u.is_superuser)(view_func)


@login_required
@staff_required
def admin_dashboard(request):
    salas = Sala.objects.annotate(total_reservas=Count('agendamento')).order_by('nome')
    recent_posts = Post.objects.order_by('-created_at')[:6]
    return render(request, 'usuarios/admin_dashboard.html', {'salas': salas, 'recent_posts': recent_posts})


@login_required
@staff_required
def criar_sala(request):
    if request.method == 'POST':
        form = SalaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sala criada.')
            return redirect('admin_dashboard')
    else:
        form = SalaForm()
    return render(request, 'usuarios/admin_edit.html', {'form': form, 'title': 'Criar Sala'})


@login_required
@staff_required
def editar_sala(request, pk):
    sala = get_object_or_404(Sala, pk=pk)
    if request.method == 'POST':
        form = SalaForm(request.POST, request.FILES, instance=sala)
        if form.is_valid():
            form.save()
            messages.success(request, f'Sala "{sala.nome}" atualizada.')
            return redirect('admin_dashboard')
    else:
        form = SalaForm(instance=sala)
    return render(request, 'usuarios/admin_edit.html', {
        'form': form,
        'title': f'Editar {sala.nome}',
    })


@login_required
@staff_required
def excluir_sala(request, pk):
    sala = get_object_or_404(Sala, pk=pk)
    # Agendamento.sala usa on_delete=CASCADE: excluir a sala apaga junto
    # todas as reservas ligadas a ela, incluindo o histórico dos usuários.
    total_reservas = Agendamento.objects.filter(sala=sala).count()

    if request.method == 'POST':
        nome = sala.nome
        sala.delete()
        messages.success(request, f'Sala "{nome}" excluída.')
        return redirect('admin_dashboard')

    return render(request, 'usuarios/admin_delete.html', {
        'sala': sala,
        'total_reservas': total_reservas,
    })


@login_required
@superuser_required
def gerenciar_permissoes(request):
    q = request.GET.get('q', '').strip()

    # Handle POST actions: update or remove permissions for a user
    # Papel -> flags do Django. Professor também recebe is_staff para
    # continuar acessando o painel operacional.
    FLAGS_POR_PAPEL = {
        Profile.PROFESSOR: {'is_staff': True, 'is_superuser': True},
        Profile.BOLSISTA: {'is_staff': True, 'is_superuser': False},
        Profile.ALUNO: {'is_staff': False, 'is_superuser': False},
    }

    if request.method == 'POST':
        uid = request.POST.get('user_id')
        papel = request.POST.get('papel')

        if not uid or papel not in FLAGS_POR_PAPEL:
            messages.error(request, 'Usuário ou papel inválido.')
            return redirect('gerenciar_permissoes')

        user = get_object_or_404(User, pk=uid)

        # Um professor não pode rebaixar a si mesmo: evita o sistema
        # ficar sem ninguém capaz de gerenciar papéis.
        if user == request.user and papel != Profile.PROFESSOR:
            messages.error(request, 'Você não pode alterar seu próprio papel de professor.')
            return redirect(f"{request.path}?q={q}")

        for flag, valor in FLAGS_POR_PAPEL[papel].items():
            setattr(user, flag, valor)
        user.save()

        nome = user.get_full_name() or user.username
        messages.success(
            request,
            f'{nome} agora é {Profile.PAPEL_LABELS[papel].lower()}.',
        )
        return redirect(f"{request.path}?q={q}")

    users = User.objects.all().select_related('profile')
    if q:
        users = users.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q) | Q(profile__matricula__icontains=q)
        )
    users = users.order_by('username')[:200]

    return render(request, 'usuarios/admin_permissions.html', {
        'users': users,
        'q': q,
        'total_professores': User.objects.filter(is_superuser=True).count(),
        'total_bolsistas': User.objects.filter(is_staff=True, is_superuser=False).count(),
        'total_alunos': User.objects.filter(is_staff=False, is_superuser=False).count(),
    })


@login_required
@staff_required
def criar_postagem(request):
    """Criar postagem rápida a partir do painel administrativo centralizado."""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            p = form.save(commit=False)
            p.author = request.user
            if p.is_published and not p.published_at:
                from django.utils import timezone
                p.published_at = timezone.now()
            p.save()
            return redirect('admin_dashboard')
    else:
        form = PostForm()
    return render(request, 'usuarios/admin_edit.html', {'form': form, 'title': 'Criar Postagem'})
