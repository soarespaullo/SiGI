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

    # Totais gerais
    # total_membros = Member.query.count()
    total_membros = Member.query.filter(Member.data_saida.is_(None)).count()
    total_batizados = Member.query.filter_by(batizado=True).count()
    total_dizimistas = Member.query.filter_by(dizimista=True).count()
    total_eventos = Evento.query.count()
    total_visitantes = Member.query.filter_by(visitante=True).count()  # supondo campo visitante

    # Mês/ano atual
    agora = datetime.now()
    mes_atual = agora.month
    ano_atual = agora.year

    # Mês em português sem locale
    meses_pt = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    mes_nome = meses_pt.get(mes_atual, "Mês")

    # Entradas do mês atual
    entradas_mes = (
        db.session.query(func.sum(Financeiro.valor))
        .filter(Financeiro.tipo == "Entrada")
        .filter(func.extract('month', Financeiro.data) == mes_atual)
        .filter(func.extract('year', Financeiro.data) == ano_atual)
        .scalar()
    ) or 0
    total_entradas = format_currency(entradas_mes)

    # Saídas do mês atual
    saidas_mes = (
        db.session.query(func.sum(Financeiro.valor))
        .filter(Financeiro.tipo == "Saída")
        .filter(func.extract('month', Financeiro.data) == mes_atual)
        .filter(func.extract('year', Financeiro.data) == ano_atual)
        .scalar()
    ) or 0
    total_saidas = format_currency(saidas_mes)

    # Dados financeiros últimos 6 meses (para gráfico)
    entradas = (
        db.session.query(
            func.extract('year', Financeiro.data).label("ano"),
            func.extract('month', Financeiro.data).label("mes"),
            func.sum(Financeiro.valor).label("total")
        )
        .filter(Financeiro.tipo == "Entrada")
        .group_by("ano", "mes")
        .order_by("ano", "mes")
        .limit(6)
        .all()
    )
    meses_labels = [
        f"{int(r.mes)}/{int(r.ano)}"
        for r in entradas if r.mes is not None and r.ano is not None
    ]
    financeiro_mensal = [float(r.total) for r in entradas]

    saidas = (
        db.session.query(
            func.extract('year', Financeiro.data).label("ano"),
            func.extract('month', Financeiro.data).label("mes"),
            func.sum(Financeiro.valor).label("total")
        )
        .filter(Financeiro.tipo == "Saída")
        .group_by("ano", "mes")
        .order_by("ano", "mes")
        .limit(6)
        .all()
    )
    financeiro_saidas = [float(r.total) for r in saidas]

    has_financeiro_data = bool(financeiro_mensal or financeiro_saidas)

    # Aniversariantes do mês (limitando a 5)
    proximos_aniversariantes = (
        Member.query
        .filter(func.extract('month', Member.data_nascimento) == mes_atual)
        .order_by(func.extract('day', Member.data_nascimento))
        .limit(5)
        .all()
    )


    # Crescimento da igreja (novos membros por mês/ano)
    crescimento = (
        db.session.query(
            func.extract('year', Member.data_cadastro).label("ano"),
            func.extract('month', Member.data_cadastro).label("mes"),
            func.count(Member.id).label("novos")
        )
        .filter(Member.data_cadastro.isnot(None))
        .group_by("ano", "mes")
        .order_by("ano", "mes")
        .all()
    )

    crescimento_labels = [
        f"{int(r.mes)}/{int(r.ano)}"
        for r in crescimento if r.mes is not None and r.ano is not None
    ]
    crescimento_valores = [
        int(r.novos)
        for r in crescimento if r.mes is not None and r.ano is not None
    ]

    # Organizar valores por ano (entradas e saídas) - agora com 12 meses fixos
    crescimento_valores_por_ano = {}
    for r in crescimento:
        if r.ano and r.mes:
            ano = int(r.ano)
            mes = int(r.mes)
            if ano not in crescimento_valores_por_ano:
                crescimento_valores_por_ano[ano] = [0] * 12
            crescimento_valores_por_ano[ano][mes - 1] = int(r.novos)

    # Saídas por ano (membros que saíram) - também com 12 meses fixos
    saidas_valores_por_ano = {}
    saidas_query = (
        db.session.query(
            func.extract('year', Member.data_saida).label("ano"),
            func.extract('month', Member.data_saida).label("mes"),
            func.count(Member.id).label("saidas")
        )
        .filter(Member.data_saida.isnot(None))
        .group_by("ano", "mes")
        .order_by("ano", "mes")
        .all()
    )
    for r in saidas_query:
        if r.ano and r.mes:
            ano = int(r.ano)
            mes = int(r.mes)
            if ano not in saidas_valores_por_ano:
                saidas_valores_por_ano[ano] = [0] * 12
            saidas_valores_por_ano[ano][mes - 1] = int(r.saidas)

    # Indicadores por ano
    indicadores_por_ano = {}
    anos = db.session.query(func.extract('year', Member.data_cadastro)).distinct().all()
    for (ano,) in anos:
        if ano is None:
            continue
        ano = int(ano)

        entradas = (
            db.session.query(func.count(Member.id))
            .filter(func.extract('year', Member.data_cadastro) == ano)
            .scalar()
        ) or 0

        saidas = (
            db.session.query(func.count(Member.id))
            .filter(func.extract('year', Member.data_saida) == ano)
            .scalar()
        ) or 0

        movimentacao = entradas - saidas
        taxa = None
        if total_membros > 0:
            taxa = round((movimentacao / total_membros) * 100, 1)

        # ✅ cálculo correto do total de membros naquele ano
        total_ano = (
            db.session.query(func.count(Member.id))
            .filter(func.extract('year', Member.data_cadastro) <= ano)
            .filter((Member.data_saida.is_(None)) | (func.extract('year', Member.data_saida) > ano))
            .scalar()
        ) or 0

        indicadores_por_ano[ano] = {
            "entradas": int(entradas),
            "saidas": int(saidas),
            "movimentacao": int(movimentacao),
            "taxa": float(taxa) if taxa is not None else None,
            "total_membros": int(total_ano)
        }

    # Taxa de crescimento percentual geral
    taxa_crescimento = None
    tendencia = None
    if len(crescimento_valores) >= 2:
        ultimo = crescimento_valores[-1]
        anterior = crescimento_valores[-2]
        if anterior > 0:
            taxa_crescimento = round(((ultimo - anterior) / anterior) * 100, 1)
            tendencia = "up" if taxa_crescimento > 0 else "down"


    # Eventos próximos (alerta)
    em_dois_dias = agora + timedelta(days=2)
    existe_evento = (
        Evento.query
        .filter(Evento.data_inicio <= em_dois_dias,
                Evento.data_fim >= agora)
        .first()
    )
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
        total_visitantes=total_visitantes,
        meses_labels=meses_labels,
        financeiro_mensal=financeiro_mensal,
        financeiro_saidas=financeiro_saidas,
        total_entradas=total_entradas,
        total_saidas=total_saidas,
        has_financeiro_data=has_financeiro_data,
        proximos_aniversariantes=proximos_aniversariantes,
        crescimento_labels=crescimento_labels,
        crescimento_valores=crescimento_valores,
        crescimento_valores_por_ano=crescimento_valores_por_ano,
        saidas_valores_por_ano=saidas_valores_por_ano,
        indicadores_por_ano=indicadores_por_ano,
        taxa_crescimento=taxa_crescimento,
        tendencia=tendencia,
        mes_nome=mes_nome
    )


@dashboard_bp.route("/dismiss-evento-alert")
def dismiss_evento_alert():
    session.pop("evento_alert", None)
    session.pop("evento_alert_type", None)
    session["evento_alert_dismissed"] = True
    return "", 204


@dashboard_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop("evento_alert", None)
    session.pop("evento_alert_type", None)
    session.pop("evento_alert_dismissed", None)
    flash("Logout realizado com sucesso.", "success")
    return redirect(url_for('auth.login'))
