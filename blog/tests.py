import tempfile
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from blog.models import Post

User = get_user_model()


def _tiny_gif():
    """Return a minimal valid GIF file for upload tests."""
    return (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00'
        b'\x80\x00\x00\xff\xff\xff\x00\x00\x00'
        b'\x21\xf9\x04\x00\x00\x00\x00\x00'
        b'\x2c\x00\x00\x00\x00\x01\x00\x01\x00'
        b'\x00\x02\x02\x44\x01\x00\x3b'
    )


class BlogTestMixin:
    """Shared setup: creates users and sample posts."""

    def setUp(self):
        self.client = Client()

        # Regular user (not staff)
        self.user = User.objects.create_user(
            username='regular', password='pass1234'
        )

        # Staff user (editor)
        self.staff = User.objects.create_user(
            username='editor', password='pass1234', is_staff=True
        )

        # Superuser
        self.superuser = User.objects.create_superuser(
            username='admin', password='pass1234'
        )

        # Published post
        self.published_post = Post.objects.create(
            author=self.staff,
            title='Post Publicado',
            slug='post-publicado',
            summary='Resumo do post publicado',
            content='Conteúdo completo do post publicado.',
            is_published=True,
            published_at=timezone.now(),
        )

        # Draft post (not published)
        self.draft_post = Post.objects.create(
            author=self.staff,
            title='Rascunho',
            slug='rascunho',
            summary='Resumo do rascunho',
            content='Conteúdo do rascunho.',
            is_published=False,
        )


# ============================================================
#  PUBLIC ACCESS TESTS
# ============================================================

class BlogPublicAccessTest(BlogTestMixin, TestCase):
    """Tests for public (unauthenticated) access to the blog."""

    def test_index_accessible_anonymous(self):
        """Anonymous users can view the blog index."""
        resp = self.client.get(reverse('blog_index'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Post Publicado')

    def test_index_hides_drafts(self):
        """Draft posts must NOT appear on the public index."""
        resp = self.client.get(reverse('blog_index'))
        self.assertNotContains(resp, 'Rascunho')

    def test_detail_accessible_anonymous(self):
        """Anonymous users can view a published post detail."""
        resp = self.client.get(
            reverse('blog_detail', args=[self.published_post.slug])
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Post Publicado')

    def test_detail_draft_returns_404(self):
        """Accessing a draft post via public URL should return 404."""
        resp = self.client.get(
            reverse('blog_detail', args=[self.draft_post.slug])
        )
        self.assertEqual(resp.status_code, 404)

    def test_search_filters_by_title(self):
        """The search should filter posts by title."""
        resp = self.client.get(reverse('blog_index'), {'q': 'Publicado'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Post Publicado')

    def test_search_filters_by_content(self):
        """The search should filter posts by content."""
        resp = self.client.get(reverse('blog_index'), {'q': 'completo'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Post Publicado')

    def test_search_no_results(self):
        """The search should show empty state when no matches."""
        resp = self.client.get(reverse('blog_index'), {'q': 'xyznonexistent'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Nenhum resultado encontrado')

    def test_pagination_works(self):
        """Pagination should work correctly."""
        # Create enough posts to trigger pagination (>6)
        for i in range(8):
            Post.objects.create(
                author=self.staff,
                title=f'Post Extra {i}',
                slug=f'post-extra-{i}',
                content=f'Conteúdo extra {i}',
                is_published=True,
                published_at=timezone.now(),
            )
        resp = self.client.get(reverse('blog_index'))
        self.assertEqual(resp.status_code, 200)
        # Should have pagination
        self.assertContains(resp, 'gina 1 de')

        # Page 2
        resp2 = self.client.get(reverse('blog_index'), {'page': '2'})
        self.assertEqual(resp2.status_code, 200)

    def test_empty_state_no_posts(self):
        """When there are no published posts, show empty state."""
        Post.objects.all().delete()
        resp = self.client.get(reverse('blog_index'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Nenhuma publica')


# ============================================================
#  AUTHENTICATION TESTS
# ============================================================

class BlogAuthenticationTest(BlogTestMixin, TestCase):
    """Tests that admin routes require authentication."""

    def test_admin_list_redirects_anonymous(self):
        """Anonymous user should be redirected from admin list."""
        resp = self.client.get(reverse('blog_admin'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('login', resp.url)

    def test_admin_my_posts_redirects_anonymous(self):
        """Anonymous user should be redirected from admin my posts."""
        resp = self.client.get(reverse('blog_admin_my_posts'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('login', resp.url)

    def test_admin_create_redirects_anonymous(self):
        """Anonymous user should be redirected from create."""
        resp = self.client.get(reverse('blog_admin_create'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('login', resp.url)

    def test_admin_edit_redirects_anonymous(self):
        """Anonymous user should be redirected from edit."""
        resp = self.client.get(
            reverse('blog_admin_edit', args=[self.published_post.pk])
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn('login', resp.url)

    def test_admin_delete_redirects_anonymous(self):
        """Anonymous user should be redirected from delete."""
        resp = self.client.get(
            reverse('blog_admin_delete', args=[self.published_post.pk])
        )
        self.assertEqual(resp.status_code, 302)
        self.assertIn('login', resp.url)


# ============================================================
#  AUTHORIZATION TESTS
# ============================================================

class BlogAuthorizationTest(BlogTestMixin, TestCase):
    """Tests that non-staff users cannot access admin routes."""

    def test_regular_user_cannot_access_admin_list(self):
        """Non-staff user should be denied access to admin list."""
        self.client.login(username='regular', password='pass1234')
        resp = self.client.get(reverse('blog_admin'))
        self.assertEqual(resp.status_code, 302)

    def test_regular_user_cannot_access_admin_my_posts(self):
        """Non-staff user should be denied access to admin my posts."""
        self.client.login(username='regular', password='pass1234')
        resp = self.client.get(reverse('blog_admin_my_posts'))
        self.assertEqual(resp.status_code, 302)

    def test_regular_user_cannot_create(self):
        """Non-staff user should be denied access to create."""
        self.client.login(username='regular', password='pass1234')
        resp = self.client.get(reverse('blog_admin_create'))
        self.assertEqual(resp.status_code, 302)

    def test_regular_user_cannot_edit(self):
        """Non-staff user should be denied access to edit."""
        self.client.login(username='regular', password='pass1234')
        resp = self.client.get(
            reverse('blog_admin_edit', args=[self.published_post.pk])
        )
        self.assertEqual(resp.status_code, 302)

    def test_regular_user_cannot_delete(self):
        """Non-staff user should be denied access to delete."""
        self.client.login(username='regular', password='pass1234')
        resp = self.client.get(
            reverse('blog_admin_delete', args=[self.published_post.pk])
        )
        self.assertEqual(resp.status_code, 302)

    def test_staff_can_access_admin_list(self):
        """Staff user should see the admin list."""
        self.client.login(username='editor', password='pass1234')
        resp = self.client.get(reverse('blog_admin'))
        self.assertEqual(resp.status_code, 200)

    def test_staff_can_access_admin_my_posts(self):
        """Staff user should see their own posts list."""
        self.client.login(username='editor', password='pass1234')
        resp = self.client.get(reverse('blog_admin_my_posts'))
        self.assertEqual(resp.status_code, 200)

    def test_staff_can_access_create(self):
        """Staff user should see the create form."""
        self.client.login(username='editor', password='pass1234')
        resp = self.client.get(reverse('blog_admin_create'))
        self.assertEqual(resp.status_code, 200)

    def test_staff_can_access_edit(self):
        """Staff user should see the edit form for their post."""
        self.client.login(username='editor', password='pass1234')
        resp = self.client.get(
            reverse('blog_admin_edit', args=[self.published_post.pk])
        )
        self.assertEqual(resp.status_code, 200)


# ============================================================
#  CRUD OPERATION TESTS
# ============================================================

class BlogCrudTest(BlogTestMixin, TestCase):
    """Tests for create, edit, and delete operations."""

    def test_staff_can_create_post(self):
        """Staff can create a new post via POST."""
        self.client.login(username='editor', password='pass1234')
        resp = self.client.post(reverse('blog_admin_create'), {
            'title': 'Novo Post',
            'slug': 'novo-post',
            'summary': 'Resumo novo',
            'content': 'Conteúdo do novo post.',
            'action': 'publish',
        })
        self.assertEqual(resp.status_code, 302)  # redirect on success
        self.assertTrue(Post.objects.filter(slug='novo-post').exists())
        post = Post.objects.get(slug='novo-post')
        self.assertEqual(post.author, self.staff)
        self.assertTrue(post.is_published)
        self.assertIsNotNone(post.published_at)

    def test_staff_can_edit_post(self):
        """Staff can edit their own post via POST."""
        self.client.login(username='editor', password='pass1234')
        resp = self.client.post(
            reverse('blog_admin_edit', args=[self.published_post.pk]),
            {
                'title': 'Título Atualizado',
                'slug': 'post-publicado',
                'summary': 'Resumo atualizado',
                'content': 'Conteúdo atualizado.',
                'action': 'save',
            }
        )
        self.assertEqual(resp.status_code, 302)
        self.published_post.refresh_from_db()
        self.assertEqual(self.published_post.title, 'Título Atualizado')

    def test_staff_can_delete_post(self):
        """Staff can delete their own post via POST."""
        self.client.login(username='editor', password='pass1234')
        pk = self.published_post.pk
        resp = self.client.post(
            reverse('blog_admin_delete', args=[pk])
        )
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Post.objects.filter(pk=pk).exists())

    def test_other_staff_cannot_edit_post(self):
        """Another staff user (not the author or superuser) is redirected."""
        other_staff = User.objects.create_user(
            username='other_editor', password='pass1234', is_staff=True
        )
        self.client.login(username='other_editor', password='pass1234')
        resp = self.client.post(
            reverse('blog_admin_edit', args=[self.published_post.pk]),
            {
                'title': 'Hackeado',
                'slug': 'post-publicado',
                'content': 'Conteúdo hackeado.',
            }
        )
        self.assertEqual(resp.status_code, 302)
        self.published_post.refresh_from_db()
        self.assertNotEqual(self.published_post.title, 'Hackeado')

    def test_superuser_can_edit_any_post(self):
        """Superuser should NOT be able to edit posts they didn't author."""
        self.client.login(username='admin', password='pass1234')
        resp = self.client.post(
            reverse('blog_admin_edit', args=[self.published_post.pk]),
            {
                'title': 'Editado pelo Admin',
                'slug': 'post-publicado',
                'summary': 'Atualizado pelo admin',
                'content': 'Conteúdo editado pelo admin.',
                'action': 'save',
            }
        )
        # should be redirected away (not allowed)
        self.assertEqual(resp.status_code, 302)
        self.published_post.refresh_from_db()
        # title must not have changed
        self.assertNotEqual(self.published_post.title, 'Editado pelo Admin')

    def test_publish_sets_published_at(self):
        """Setting is_published=True auto-sets published_at if not set."""
        self.client.login(username='editor', password='pass1234')
        self.client.post(reverse('blog_admin_create'), {
            'title': 'Auto Date',
            'slug': 'auto-date',
            'content': 'Testing auto date.',
            'action': 'publish',
        })
        post = Post.objects.get(slug='auto-date')
        self.assertIsNotNone(post.published_at)


# ============================================================
#  COVER IMAGE UPLOAD TESTS
# ============================================================

class BlogCoverUploadTest(BlogTestMixin, TestCase):
    """Tests for cover image upload on create and edit."""

    def test_create_with_cover_image(self):
        """Staff can create a post with a cover image."""
        self.client.login(username='editor', password='pass1234')
        cover = SimpleUploadedFile(
            name='test_cover.gif',
            content=_tiny_gif(),
            content_type='image/gif',
        )
        resp = self.client.post(reverse('blog_admin_create'), {
            'title': 'Post com Capa',
            'slug': 'post-com-capa',
            'content': 'Post com imagem de capa.',
            'cover': cover,
            'is_published': True,
        })
        self.assertEqual(resp.status_code, 302)
        post = Post.objects.get(slug='post-com-capa')
        self.assertTrue(post.cover)
        self.assertIn('blog/covers/', post.cover.name)

    def test_edit_replaces_cover_image(self):
        """Staff can replace the cover image on an existing post."""
        self.client.login(username='editor', password='pass1234')
        cover = SimpleUploadedFile(
            name='new_cover.gif',
            content=_tiny_gif(),
            content_type='image/gif',
        )
        resp = self.client.post(
            reverse('blog_admin_edit', args=[self.published_post.pk]),
            {
                'title': self.published_post.title,
                'slug': self.published_post.slug,
                'content': self.published_post.content,
                'cover': cover,
                'is_published': True,
            }
        )
        self.assertEqual(resp.status_code, 302)
        self.published_post.refresh_from_db()
        self.assertTrue(self.published_post.cover)

    def test_create_without_cover_succeeds(self):
        """Creating a post without a cover image should succeed."""
        self.client.login(username='editor', password='pass1234')
        resp = self.client.post(reverse('blog_admin_create'), {
            'title': 'Post sem Capa',
            'slug': 'post-sem-capa',
            'content': 'Post sem imagem de capa.',
            'is_published': True,
        })
        self.assertEqual(resp.status_code, 302)
        post = Post.objects.get(slug='post-sem-capa')
        self.assertFalse(bool(post.cover))


# ============================================================
#  ORDERING TESTS
# ============================================================

class BlogOrderingTest(BlogTestMixin, TestCase):
    """Tests that posts are ordered by published date."""

    def test_posts_ordered_by_published_at_desc(self):
        """Posts should appear newest first on the index."""
        old_post = Post.objects.create(
            author=self.staff,
            title='Post Antigo',
            slug='post-antigo',
            content='Antigo',
            is_published=True,
            published_at=timezone.now() - timezone.timedelta(days=30),
        )
        new_post = Post.objects.create(
            author=self.staff,
            title='Post Novo',
            slug='post-novo',
            content='Novo',
            is_published=True,
            published_at=timezone.now(),
        )

        resp = self.client.get(reverse('blog_index'))
        content = resp.content.decode()
        pos_new = content.find('Post Novo')
        pos_old = content.find('Post Antigo')
        # Newer post should appear before older post
        self.assertLess(pos_new, pos_old)
