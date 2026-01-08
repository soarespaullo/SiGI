from flask import Blueprint, render_template, session, flash, redirect, url_for
from app.models import Member, Evento, Financeiro
from app.extensions import db
from sqlalchemy import func
from datetime import datetime, timedelta
from flask_login import login_required, current_user, logout_user

dashboard_bp = Blueprint('dashboard', __name__)

def format_currency(value):
    """Formata número como moeda brasileira R$ 1.234,56"""
    if value is None:
        return "R$ 0,00"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    user = current_user
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

    # 🔹 Verificação de eventos próximos (em andamento ou até 2 dias à frente)
    agora = datetime.now()
    em_dois_dias = agora + timedelta(days=2)

    existe_evento = (
        Evento.query
        .filter(Evento.data_inicio <= em_dois_dias,   # começa até 2 dias à frente
                Evento.data_fim >= agora)            # ainda não terminou
        .first()
    )

    # Só grava o alerta se ainda não existir e não tiver sido fechado
    if existe_evento and not session.get("evento_alert") and not session.get("evento_alert_dismissed"):
        session["evento_alert"] = "⚠️ Há eventos próximos ou em andamento nos próximos 2 dias. Clique aqui para ver todos."
        session["evento_alert_type"] = "warning"

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
    # Remove o alerta da sessão ao clicar no X e marca como fechado
    session.pop("evento_alert", None)
    session.pop("evento_alert_type", None)
    session["evento_alert_dismissed"] = True
    return "", 204

@dashboard_bp.route("/logout")
@login_required
def logout():
    logout_user()
    # Limpa alertas ao sair
    session.pop("evento_alert", None)
    session.pop("evento_alert_type", None)
    session.pop("evento_alert_dismissed", None)
    flash("Logout realizado com sucesso.", "success")
    return redirect(url_for('auth.login'))
