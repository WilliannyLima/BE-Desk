from notificacoes.models import Notificacao


def criar_notificacao(destinatario, titulo, mensagem, tipo='SISTEMA', link=''):
    return Notificacao.objects.create(
        destinatario=destinatario,
        titulo=titulo,
        mensagem=mensagem,
        tipo=tipo,
        link=link,
    )


def notificar_reserva_criada(agendamento):
    from django.contrib.auth.models import User
    admins = User.objects.filter(is_staff=True, is_active=True)
    for admin in admins:
        criar_notificacao(
            destinatario=admin,
            titulo='Nova solicitação de reserva',
            mensagem=f'{agendamento.usuario.get_full_name() or agendamento.usuario.username} solicitou a sala "{agendamento.sala.nome}" para {agendamento.data_inicio.strftime("%d/%m/%Y")} às {agendamento.horario.strftime("%H:%M")}.',
            tipo='ADMIN_NOVA_SOLICITACAO',
            link='/gerenciar/',
        )
    criar_notificacao(
        destinatario=agendamento.usuario,
        titulo='Reserva enviada',
        mensagem=f'Sua reserva para a sala "{agendamento.sala.nome}" em {agendamento.data_inicio.strftime("%d/%m/%Y")} às {agendamento.horario.strftime("%H:%M")} foi enviada e está pendente de aprovação.',
        tipo='RESERVA_CRIADA',
        link='/reservas/',
    )


def notificar_reserva_aprovada(agendamento):
    criar_notificacao(
        destinatario=agendamento.usuario,
        titulo='Reserva aprovada',
        mensagem=f'Sua reserva para a sala "{agendamento.sala.nome}" em {agendamento.data_inicio.strftime("%d/%m/%Y")} às {agendamento.horario.strftime("%H:%M")} foi aprovada.',
        tipo='RESERVA_APROVADA',
        link='/reservas/',
    )


def notificar_reserva_rejeitada(agendamento):
    criar_notificacao(
        destinatario=agendamento.usuario,
        titulo='Reserva rejeitada',
        mensagem=f'Sua reserva para a sala "{agendamento.sala.nome}" em {agendamento.data_inicio.strftime("%d/%m/%Y")} às {agendamento.horario.strftime("%H:%M")} foi rejeitada.',
        tipo='RESERVA_REJEITADA',
        link='/reservas/',
    )


def notificar_reserva_cancelada(agendamento):
    from django.contrib.auth.models import User
    admins = User.objects.filter(is_staff=True, is_active=True)
    for admin in admins:
        criar_notificacao(
            destinatario=admin,
            titulo='Reserva cancelada',
            mensagem=f'{agendamento.usuario.get_full_name() or agendamento.usuario.username} cancelou a reserva da sala "{agendamento.sala.nome}" para {agendamento.data_inicio.strftime("%d/%m/%Y")}.',
            tipo='RESERVA_CANCELADA',
            link='/gerenciar/',
        )


def notificar_recurso_criado(reserva_recurso):
    from django.contrib.auth.models import User
    admins = User.objects.filter(is_staff=True, is_active=True)
    for admin in admins:
        criar_notificacao(
            destinatario=admin,
            titulo='Nova solicitação de recurso',
            mensagem=f'{reserva_recurso.usuario.get_full_name() or reserva_recurso.usuario.username} solicitou o recurso "{reserva_recurso.recurso.nome}".',
            tipo='ADMIN_NOVA_SOLICITACAO',
            link='/gerenciar/',
        )
    criar_notificacao(
        destinatario=reserva_recurso.usuario,
        titulo='Solicitação de recurso enviada',
        mensagem=f'Sua solicitação para o recurso "{reserva_recurso.recurso.nome}" foi enviada e está pendente de aprovação.',
        tipo='RECURSO_CRIADO',
        link='/recursos/',
    )


def notificar_recurso_aprovado(reserva_recurso):
    criar_notificacao(
        destinatario=reserva_recurso.usuario,
        titulo='Recurso aprovado',
        mensagem=f'Sua solicitação para o recurso "{reserva_recurso.recurso.nome}" foi aprovada.',
        tipo='RECURSO_APROVADO',
        link='/recursos/',
    )


def notificar_recurso_rejeitado(reserva_recurso):
    criar_notificacao(
        destinatario=reserva_recurso.usuario,
        titulo='Recurso rejeitado',
        mensagem=f'Sua solicitação para o recurso "{reserva_recurso.recurso.nome}" foi rejeitada.',
        tipo='RECURSO_REJEITADO',
        link='/recursos/',
    )


def notificar_lembrete(usuario, agendamento):
    criar_notificacao(
        destinatario=usuario,
        titulo='Lembrete de reserva',
        mensagem=f'Você tem uma reserva para a sala "{agendamento.sala.nome}" em {agendamento.data_inicio.strftime("%d/%m/%Y")} às {agendamento.horario.strftime("%H:%M")}.',
        tipo='LEMBRETE',
        link='/reservas/',
    )
