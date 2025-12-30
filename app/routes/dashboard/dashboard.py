from flask import Blueprint, render_template, session, flash
from app.models import User, Member, Evento, Financeiro   # ✅ importa models do pacote app.models
from app.extensions import db                             # ✅ importa db da extensions.py
from sqlalchemy import func
from datetime import datetime, timedelta
from flask_login import login_required, current_user      # 👈 importa login_required e current_user

dashboard_bp = Blueprint('dashboard', __name__)

def format_currency(value):
    """Formata número como moeda brasileira R$ 1.234,56"""
    if value is None:
        return "R$ 0,00"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@dashboard_bp.route('/dashboard')
@login_required  # 👈 protege a rota
def dashboard():
    # Usa current_user do Flask-Login em vez de session['user_id']
    user = current_user

    # Define o nome do usuário
    user_name = user.nome if user.nome else user.email.split('@')[0].capitalize()

    # Totais de membros e eventos
    total_membros = Member.query.count()
    total_batizados = Member.query.filter_by(batizado=True).count()
    total_dizimistas = Member.query.filter_by(dizimista=True).count()
    total_eventos = Evento.query.count()

    # Entradas por mês (últimos 6 meses)
    entradas = (
        db.session.query(
            func.extract('month', Financeiro.data).label("mes"),
            func.sum(Financeiro.valor).label("total")
        )
        .filter(Financeiro.tipo == "Entrada")
        .group_by("mes")
        .order_by("mes")
        .limit(6)
        .all()
    )
    meses_labels = [int(r.mes) for r in entradas]
    financeiro_mensal = [float(r.total) for r in entradas]

    # Saídas por mês (últimos 6 meses)
    saidas = (
        db.session.query(
            func.extract('month', Financeiro.data).label("mes"),
            func.sum(Financeiro.valor).label("total")
        )
        .filter(Financeiro.tipo == "Saída")
        .group_by("mes")
        .order_by("mes")
        .limit(6)
        .all()
    )
    financeiro_saidas = [float(r.total) for r in saidas]
    total_saidas_valor = sum(financeiro_saidas) if saidas else 0
    total_saidas = format_currency(total_saidas_valor)

    has_financeiro_data = bool(financeiro_mensal or financeiro_saidas)

    # Aniversariantes do mês
    mes_atual = datetime.now().month
    proximos_aniversariantes = (
        Member.query
        .filter(func.extract('month', Member.data_nascimento) == mes_atual)
        .order_by(func.extract('day', Member.data_nascimento))
        .all()
    )

    # 🔹 Verificação de eventos próximos (nos próximos 2 dias)
    if not session.get("evento_alert") and not session.get("evento_alert_shown"):
        agora = datetime.now()
        existe_evento = (
            Evento.query
            .filter(Evento.data_inicio >= agora,
                    Evento.data_inicio <= agora + timedelta(days=2))
            .first()
        )
        if existe_evento:
            session["evento_alert"] = "⚠️ Há eventos próximos nos próximos 2 dias. Clique aqui para ver todos."
            session["evento_alert_type"] = "warning"
            session["evento_alert_shown"] = True

    return render_template(
        'dashboard/dashboard.html',
        user_name=user_name,
        total_membros=total_membros,
        total_batizados=total_batizados,
        total_dizimistas=total_dizimistas,
        total_eventos=total_eventos,
        meses_labels=meses_labels,
        financeiro_mensal=financeiro_mensal,
        financeiro_saidas=financeiro_saidas,
        total_saidas=total_saidas,
        has_financeiro_data=has_financeiro_data,
        proximos_aniversariantes=proximos_aniversariantes
    )

@dashboard_bp.route("/dismiss-evento-alert")
def dismiss_evento_alert():
    session.pop("evento_alert", None)
    return "", 204
