from django.urls import path

from materiais.views.materiais import lista_recursos, reservar_recurso

urlpatterns = [
    path("recursos/", lista_recursos, name="lista_recursos"),
    path("recursos/reservar/<int:recurso_id>/", reservar_recurso, name="reservar_recurso"),
]
