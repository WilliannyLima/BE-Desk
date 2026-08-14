from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from bedesk.models import Sala, Profile
from usuarios.forms_admin import SalaForm, PermissionForm
from blog.models import Post
from blog.forms import PostForm
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404

User = get_user_model()


def staff_required(view_func):
    return user_passes_test(lambda u: u.is_active and u.is_staff)(view_func)


def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_active and u.is_superuser)(view_func)


@login_required
@staff_required
def admin_dashboard(request):
    salas = Sala.objects.all()
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
@superuser_required
def gerenciar_permissoes(request):
    q = request.GET.get('q', '').strip()

    # Handle POST actions: update or remove permissions for a user
    if request.method == 'POST':
        action = request.POST.get('action')
        uid = request.POST.get('user_id')
        if not uid:
            messages.error(request, 'Usuário inválido.')
            return redirect('gerenciar_permissoes')
        user = get_object_or_404(User, pk=uid)
        if action == 'update':
            is_staff = True if request.POST.get('is_staff') == 'on' else False
            is_super = True if request.POST.get('is_superuser') == 'on' else False
            # prevent removing own superuser flag accidentally
            if user == request.user and not is_super:
                messages.error(request, 'Você não pode remover seu próprio acesso de superusuário.')
                return redirect('gerenciar_permissoes')
            user.is_staff = is_staff
            user.is_superuser = is_super
            user.save()
            messages.success(request, f'Permissões atualizadas para {user.username}.')
            return redirect(f"{request.path}?q={q}")
        elif action == 'remove':
            # Clear permissions
            if user == request.user:
                messages.error(request, 'Você não pode remover suas próprias permissões aqui.')
                return redirect('gerenciar_permissoes')
            user.is_staff = False
            user.is_superuser = False
            user.save()
            messages.success(request, f'Permissões removidas de {user.username}.')
            return redirect(f"{request.path}?q={q}")

    users = User.objects.all().select_related('profile')
    if q:
        users = users.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q) | Q(profile__matricula__icontains=q)
        )
    users = users.order_by('username')[:200]

    return render(request, 'usuarios/admin_permissions.html', {'users': users, 'q': q})


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
