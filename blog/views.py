from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Q

from .models import Post
from .forms import PostForm


def is_editor(user):
    return user.is_active and user.is_staff


def blog_index(request):
    q = request.GET.get('q', '').strip()
    posts = Post.objects.filter(is_published=True)
    if q:
        posts = posts.filter(Q(title__icontains=q) | Q(summary__icontains=q) | Q(content__icontains=q))

    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/index.html', {'page_obj': page_obj, 'q': q})


def blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    return render(request, 'blog/detail.html', {'post': post})


@login_required
@user_passes_test(is_editor)
def admin_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'blog/admin_list.html', {'posts': posts})


@login_required
@user_passes_test(is_editor)
def admin_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            p = form.save(commit=False)
            p.author = request.user
            if p.is_published and not p.published_at:
                p.published_at = timezone.now()
            p.save()
            return redirect('blog_admin')
    else:
        form = PostForm()
    return render(request, 'blog/admin_edit.html', {'form': form, 'title': 'Criar Post'})


@login_required
@user_passes_test(is_editor)
def admin_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # only author or staff can edit
    if not (request.user == post.author or request.user.is_superuser):
        return redirect('blog_admin')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            p = form.save(commit=False)
            if p.is_published and not p.published_at:
                p.published_at = timezone.now()
            p.save()
            return redirect('blog_admin')
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/admin_edit.html', {'form': form, 'title': 'Editar Post'})


@login_required
@user_passes_test(is_editor)
def admin_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if not (request.user == post.author or request.user.is_superuser):
        return redirect('blog_admin')
    if request.method == 'POST':
        post.delete()
        return redirect('blog_admin')
    return render(request, 'blog/admin_delete.html', {'post': post})
