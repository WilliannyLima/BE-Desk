from django.urls import path
from integracao_suap.views import rh_eu
from integracao_suap.views import debug_token

urlpatterns = [
    path('api/rh/eu/', rh_eu, name='integracao_rh_eu'),
    path('debug-token/', debug_token, name='integracao_debug_token'),
]
