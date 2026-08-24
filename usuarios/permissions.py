"""Papéis do BE-Desk.

Professor  -> is_superuser (também recebe is_staff)
Bolsista   -> is_staff
Aluno      -> nenhuma flag

Só o professor gerencia papéis; o bolsista faz o resto da operação
(aprovar reservas, cadastrar locais, publicar no blog).
"""


def is_admin_or_staff(user):
    """Professor ou bolsista — quem opera o sistema."""
    return user.is_staff or user.is_superuser


def is_professor(user):
    return user.is_active and user.is_superuser


def is_bolsista(user):
    return user.is_active and user.is_staff and not user.is_superuser


def is_aluno(user):
    return user.is_active and not user.is_staff and not user.is_superuser
