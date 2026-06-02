from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from bedesk.models import Sala, Recurso
from usuarios.forms_admin import SalaForm, RecursoForm, PermissionForm


def staff_required(view_func):
    return user_passes_test(lambda u: u.is_active and u.is_staff)(view_func)


@login_required
@staff_required
def admin_dashboard(request):
    salas = Sala.objects.all()
    recursos = Recurso.objects.all()
    return render(request, 'usuarios/admin_dashboard.html', {'salas': salas, 'recursos': recursos})


@login_required
@staff_required
def criar_sala(request):
    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sala criada.')
            return redirect('admin_dashboard')
    else:
        form = SalaForm()
    return render(request, 'usuarios/admin_edit.html', {'form': form, 'title': 'Criar Sala'})


@login_required
@staff_required
def criar_recurso(request):
    if request.method == 'POST':
        form = RecursoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recurso criado.')
            return redirect('admin_dashboard')
    else:
        form = RecursoForm()
    return render(request, 'usuarios/admin_edit.html', {'form': form, 'title': 'Criar Recurso'})


@login_required
@staff_required
def gerenciar_permissoes(request):
    if request.method == 'POST':
        form = PermissionForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            user.is_staff = form.cleaned_data['is_staff']
            user.is_superuser = form.cleaned_data['is_superuser']
            user.save()
            messages.success(request, 'Permissões atualizadas.')
            return redirect('admin_dashboard')
    else:
        form = PermissionForm()
    return render(request, 'usuarios/admin_edit.html', {'form': form, 'title': 'Gerenciar Permissões'})
