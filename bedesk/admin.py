from django.contrib import admin
from .models import Sala, Agendamento, Recurso, ReservaRecurso

# Modelos que você já tinha (para garantir que estejam registrados)
admin.site.register(Sala)
admin.site.register(Agendamento)

# --- REGISTRO DOS NOVOS MODELOS ---
admin.site.register(Recurso)
admin.site.register(ReservaRecurso)