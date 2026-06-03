from django.db import models
from django.conf import settings
from django.urls import reverse


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
