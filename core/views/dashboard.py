import datetime
import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.db.models.functions import ExtractWeekDay, TruncMonth
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from bedesk.models import Agendamento, Recurso, ReservaRecurso, Sala
from usuarios.permissions import is_admin_or_staff

STATUS_GERENCIAVEIS = ["APROVADO", "REJEITADO"]


@login_required
@user_passes_test(is_admin_or_staff)
def gerenciar_reservas(request):
    # --- KPIs ---
    total_agendamentos = Agendamento.objects.count()
    total_recursos = ReservaRecurso.objects.count()
    total_reservas = total_agendamentos + total_recursos
    
    locais_ativos = Sala.objects.count()
    materiais_cadastrados = Recurso.objects.count()
    
    pendencias_agendamentos = Agendamento.objects.filter(status="PENDENTE").count()
    pendencias_recursos = ReservaRecurso.objects.filter(status="PENDENTE").count()
    total_pendencias = pendencias_agendamentos + pendencias_recursos
    
    if total_agendamentos > 0:
        aprovados = Agendamento.objects.filter(status="APROVADO").count()
        taxa_ocupacao = int((aprovados / total_agendamentos) * 100)
    else:
        taxa_ocupacao = 0

    # --- Charts Data ---
    # 1. Materiais mais solicitados (Top 5)
    top_materiais = ReservaRecurso.objects.values('recurso__nome').annotate(total=Count('id')).order_by('-total')[:5]
    mat_labels = [m['recurso__nome'] for m in top_materiais]
    mat_data = [m['total'] for m in top_materiais]

    # 2. Locais mais utilizados (Top 5)
    top_locais = Agendamento.objects.filter(sala__isnull=False).values('sala__nome').annotate(total=Count('id')).order_by('-total')[:5]
    locais_labels = [l['sala__nome'] for l in top_locais]
    locais_data = [l['total'] for l in top_locais]
    
    # 3. Status das reservas (All)
    status_counts = {'PENDENTE': 0, 'APROVADO': 0, 'REJEITADO': 0}
    for ag in Agendamento.objects.values('status').annotate(total=Count('id')):
        status_counts[ag['status']] = status_counts.get(ag['status'], 0) + ag['total']
    for rr in ReservaRecurso.objects.values('status').annotate(total=Count('id')):
        status_counts[rr['status']] = status_counts.get(rr['status'], 0) + rr['total']
        
    status_labels = ['Confirmadas', 'Pendentes', 'Canceladas/Rejeitadas']
    status_data = [status_counts.get('APROVADO', 0), status_counts.get('PENDENTE', 0), status_counts.get('REJEITADO', 0)]

    # 4. Reservas por Mês (Últimos 6 meses)
    hoje = datetime.date.today()
    seis_meses_atras = hoje - datetime.timedelta(days=180)
    
    meses_nomes = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    meses_labels = []
    meses_dict = {}
    curr_date = seis_meses_atras.replace(day=1)
    
    for _ in range(7):
        if curr_date > hoje:
            break
        key = f"{curr_date.year}-{curr_date.month:02d}"
        meses_dict[key] = 0
        meses_labels.append(meses_nomes[curr_date.month - 1])
        if curr_date.month == 12:
            curr_date = curr_date.replace(year=curr_date.year+1, month=1)
        else:
            curr_date = curr_date.replace(month=curr_date.month+1)
            
    meses_labels = meses_labels[-6:]
    keys_list = list(meses_dict.keys())[-6:]
    
    ag_mensal = Agendamento.objects.filter(data_inicio__gte=seis_meses_atras).annotate(month=TruncMonth('data_inicio')).values('month').annotate(total=Count('id'))
    for item in ag_mensal:
        if item['month']:
            key = f"{item['month'].year}-{item['month'].month:02d}"
            if key in meses_dict:
                meses_dict[key] += item['total']
                
    rr_mensal = ReservaRecurso.objects.filter(data_prevista__gte=seis_meses_atras).annotate(month=TruncMonth('data_prevista')).values('month').annotate(total=Count('id'))
    for item in rr_mensal:
        if item['month']:
            key = f"{item['month'].year}-{item['month'].month:02d}"
            if key in meses_dict:
                meses_dict[key] += item['total']
                
    meses_data = [meses_dict[k] for k in keys_list]

    # 5. Ocupação por Dia da Semana
    weekday_dict = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 1: 0}
    ag_dias = Agendamento.objects.filter(data_inicio__isnull=False).annotate(weekday=ExtractWeekDay('data_inicio')).values('weekday').annotate(total=Count('id'))
    for item in ag_dias:
        weekday_dict[item['weekday']] += item['total']
        
    dia_labels = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    dia_data = [weekday_dict[2], weekday_dict[3], weekday_dict[4], weekday_dict[5], weekday_dict[6], weekday_dict[7], weekday_dict[1]]

    context = {
        "salas_pendentes": Agendamento.objects.filter(status="PENDENTE", sala__isnull=False),
        "recursos_pendentes": ReservaRecurso.objects.filter(status="PENDENTE"),
        "salas_aprovadas": Agendamento.objects.filter(status="APROVADO", sala__isnull=False),
        "recursos_aprovados": ReservaRecurso.objects.filter(status="APROVADO"),
        
        "kpi_total_reservas": total_reservas,
        "kpi_locais_ativos": locais_ativos,
        "kpi_taxa_ocupacao": taxa_ocupacao,
        "kpi_pendencias": total_pendencias,
        "kpi_materiais": materiais_cadastrados,
        
        "mat_labels": json.dumps(mat_labels),
        "mat_data": json.dumps(mat_data),
        "locais_labels": json.dumps(locais_labels),
        "locais_data": json.dumps(locais_data),
        "status_labels": json.dumps(status_labels),
        "status_data": json.dumps(status_data),
        "meses_labels": json.dumps(meses_labels),
        "meses_data": json.dumps(meses_data),
        "dia_labels": json.dumps(dia_labels),
        "dia_data": json.dumps(dia_data),
    }
    return render(request, "core/gerenciar.html", context)


@user_passes_test(is_admin_or_staff)
@require_POST
def mudar_status_reserva(request, agendamento_id, novo_status):
    if novo_status not in STATUS_GERENCIAVEIS:
        return JsonResponse({"success": False, "erro": "Status inválido"}, status=400)

    reserva = get_object_or_404(Agendamento, pk=agendamento_id)
    reserva.status = novo_status
    reserva.save()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "id": reserva.id,
                "novo_status": reserva.status,
                "usuario": reserva.usuario.username,
            }
        )
    return redirect("listar_pendentes")


@user_passes_test(is_admin_or_staff)
@require_POST
def mudar_status_recurso(request, reserva_id, novo_status):
    reserva = get_object_or_404(ReservaRecurso, pk=reserva_id)

    if novo_status not in STATUS_GERENCIAVEIS:
        messages.error(request, "Status inválido.")
        return redirect("listar_pendentes")

    reserva.status = novo_status
    reserva.save()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "id": reserva.id,
                "novo_status": reserva.status,
                "usuario": reserva.usuario.username,
            }
        )

    if novo_status == "APROVADO":
        messages.success(request, f"Recurso de {reserva.usuario.username} APROVADO!")
    else:
        messages.warning(request, f"Recurso de {reserva.usuario.username} REJEITADO.")

    return redirect("listar_pendentes")
