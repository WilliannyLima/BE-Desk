from django.contrib import admin
from django.urls import include, path
from usuarios.views.accounts import logar

urlpatterns = [
    path("admin/", admin.site.urls),
    # Override the default login view to use our custom SUAP integration
    path("accounts/login/", logar, name="login"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("core.urls")),
    path("", include("usuarios.urls")),
    path("", include("reservas.urls")),
    path("", include("materiais.urls")),
    path("", include("notificacoes.urls")),
    path("", include("relatorios.urls")),
    path("", include("integracao_suap.urls")),
]
