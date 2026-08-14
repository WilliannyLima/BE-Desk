from django.urls import path
from integracao_suap.views import rh_eu
from integracao_suap.views import debug_token
from integracao_suap.views import suap_login_oauth, suap_callback

urlpatterns = [
    path('api/rh/eu/', rh_eu, name='integracao_rh_eu'),
    path('debug-token/', debug_token, name='integracao_debug_token'),
    path('login/', suap_login_oauth, name='suap_login_oauth'),
    path('auth/callback/', suap_callback, name='suap_callback'),
]
