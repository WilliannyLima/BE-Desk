from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify


def _generate_unique_slug(instance, value):
    """Generate a unique slug for the given model instance and value.
    Appends a counter suffix if the slug already exists.
    """
    base = slugify(value)[:240] or 'post'
    slug = base
    Model = instance.__class__
    counter = 1
    # exclude the current instance when editing
    while Model.objects.filter(slug=slug).exclude(pk=getattr(instance, 'pk', None)).exists():
        counter += 1
        slug = f"{base}-{counter}"
    return slug


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=260, unique=True)
    summary = models.TextField(blank=True)
    content = models.TextField()
    cover = models.ImageField(upload_to='blog/covers/', null=True, blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        # Auto-generate slug from title when missing
        if not self.slug:
            self.slug = _generate_unique_slug(self, self.title)
        super().save(*args, **kwargs)
