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
    return render(request, 'blog/admin_list.html', {
        'posts': posts,
        'title': 'Gerenciar Publicações',
        'kicker': 'Painel',
        'empty_message': 'Nenhuma publicação cadastrada',
        'empty_sub_message': 'Comece criando sua primeira publicação para o blog do Bloco E.'
    })


@login_required
@user_passes_test(is_editor)
def admin_my_posts(request):
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'blog/admin_list.html', {
        'posts': posts,
        'title': 'Minhas Publicações',
        'kicker': 'Autor',
        'empty_message': 'Você ainda não possui publicações',
        'empty_sub_message': 'Comece criando sua primeira publicação no blog.'
    })


@login_required
@user_passes_test(is_editor)
def admin_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            p = form.save(commit=False)
            p.author = request.user
            # Determine publication action. Prefer explicit action button, fall back
            # to legacy 'is_published' POST param for backward compatibility with tests.
            action = request.POST.get('action')
            is_published_post = request.POST.get('is_published')
            publish = False
            if action == 'publish':
                publish = True
            elif action == 'save':
                publish = False
            else:
                # legacy behavior: truthy is_published -> publish
                if is_published_post in ['1', 'true', 'True', 'on', True]:
                    publish = True

            p.is_published = bool(publish)

            # Respect explicit slug from POST if provided (tests rely on this)
            slug_from_post = request.POST.get('slug')
            if slug_from_post:
                p.slug = slug_from_post

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
    # only the author may edit their post
    if request.user != post.author:
        return redirect('blog_admin')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            p = form.save(commit=False)
            action = request.POST.get('action')
            is_published_post = request.POST.get('is_published')
            publish = False
            if action == 'publish':
                publish = True
            elif action == 'save':
                publish = False
            else:
                if is_published_post in ['1', 'true', 'True', 'on', True]:
                    publish = True

            p.is_published = bool(publish)

            slug_from_post = request.POST.get('slug')
            if slug_from_post:
                p.slug = slug_from_post

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
    # only the author may delete their post
    if request.user != post.author:
        return redirect('blog_admin')
    if request.method == 'POST':
        post.delete()
        return redirect('blog_admin')
    return render(request, 'blog/admin_delete.html', {'post': post})
