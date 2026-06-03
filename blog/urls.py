from django.urls import path
from . import views

urlpatterns = [
    path('blog/', views.blog_index, name='blog_index'),
    # admin routes must come before the slug route to avoid being captured as a slug
    path('blog/admin/', views.admin_list, name='blog_admin'),
    path('blog/admin/novo/', views.admin_create, name='blog_admin_create'),
    path('blog/admin/<int:pk>/editar/', views.admin_edit, name='blog_admin_edit'),
    path('blog/admin/<int:pk>/excluir/', views.admin_delete, name='blog_admin_delete'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
]
