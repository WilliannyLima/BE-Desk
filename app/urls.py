from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.index, name='login'),  # aqui chama sua view
]