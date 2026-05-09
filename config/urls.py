from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("core.urls")),
    path("", include("usuarios.urls")),
    path("", include("reservas.urls")),
    path("", include("materiais.urls")),
    path("", include("notificacoes.urls")),
    path("", include("relatorios.urls")),
    path("", include("integracao_suap.urls")),
]
