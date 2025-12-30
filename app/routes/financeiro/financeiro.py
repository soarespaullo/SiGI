from flask import Blueprint, render_template, redirect, url_for, flash, request, Response, current_app
from datetime import datetime, date
from collections import defaultdict
import csv, io, os
from werkzeug.utils import secure_filename

from app.extensions import db                   # ✅ importa db da extensions.py
from app.models import Financeiro               # ✅ importa Financeiro do pacote app.models
from app.routes.financeiro.forms import (       # ✅ ajusta para app.routes
    EntradaForm, SaidaForm, FiltroRelatorioForm, ComprovanteForm
)
from flask_login import login_required          # 👈 protege rotas com Flask-Login

financeiro_bp = Blueprint("financeiro", __name__, url_prefix="/financeiro")

# ➡️ Filtro Jinja para moeda
@financeiro_bp.app_template_filter('currency')
def currency_format(value):
    if value is None:
        return "R$ 0,00"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@financeiro_bp.route('/')
@login_required   # 👈 protege a rota
def financeiro():
    # Resumo: totais
    total_entradas = db.session.query(db.func.coalesce(db.func.sum(Financeiro.valor), 0.0)).filter(Financeiro.tipo=="Entrada").scalar()
    total_saidas = db.session.query(db.func.coalesce(db.func.sum(Financeiro.valor), 0.0)).filter(Financeiro.tipo=="Saída").scalar()
    saldo = (total_entradas or 0.0) - (total_saidas or 0.0)

    # Gráficos por mês (últimos 6 meses)
    def month_key(d: date):
        return d.strftime("%m-%Y")

    ultimos = sorted({month_key(r.data) for r in Financeiro.query.all()}, key=lambda x: datetime.strptime("01-"+x, "%d-%m-%Y"))[-6:]

    por_mes = {m: {"Entradas": 0.0, "Saídas": 0.0} for m in ultimos}
    for r in Financeiro.query.all():
        mk = month_key(r.data)
        if mk in por_mes:
            if r.tipo == "Entrada":
                por_mes[mk]["Entradas"] += float(r.valor)
            elif r.tipo == "Saída":
                por_mes[mk]["Saídas"] += float(r.valor)

    labels = ultimos
    entradas_data = [por_mes[m]["Entradas"] for m in labels]
    saidas_data = [por_mes[m]["Saídas"] for m in labels]

    return render_template(
        'financeiro/financeiro.html',
        total_entradas=total_entradas or 0.0,
        total_saidas=total_saidas or 0.0,
        saldo=saldo or 0.0,
        labels=labels,
        entradas_data=entradas_data,
        saidas_data=saidas_data
    )

@financeiro_bp.route('/entradas', methods=['GET', 'POST'])
@login_required   # 👈 protege a rota
def entradas():
    form = EntradaForm()
    if form.validate_on_submit():
        raw_valor = request.form.get('valor', '')
        valor_float = float(str(raw_valor).replace(',', '.'))

        nova = Financeiro(
            tipo="Entrada",
            categoria=form.tipo_receita.data,
            valor=valor_float,
            data=form.data.data,
            descricao=form.descricao.data,
            conta=form.conta.data
        )
        db.session.add(nova)
        db.session.commit()
        flash("Entrada registrada com sucesso!", "success")
        return redirect(url_for('financeiro.entradas'))

    registros = Financeiro.query.filter_by(tipo="Entrada").order_by(Financeiro.data.desc()).all()
    return render_template('financeiro/entradas.html', form=form, entradas=registros)

@financeiro_bp.route('/entradas/excluir/<int:id>', methods=['POST'])
@login_required   # 👈 protege a rota
def excluir_entrada(id):
    entrada = Financeiro.query.get_or_404(id)
    if entrada.tipo != "Entrada":
        flash("Registro inválido para exclusão.", "danger")
        return redirect(url_for('financeiro.entradas'))

    try:
        db.session.delete(entrada)
        db.session.commit()
        flash("Entrada excluída com sucesso!", "success")
    except Exception:
        db.session.rollback()
        flash("Erro ao excluir entrada.", "danger")

    return redirect(url_for('financeiro.entradas'))

# ➡️ Nova rota para editar Entrada
@financeiro_bp.route('/entradas/editar/<int:id>', methods=['GET', 'POST'])
@login_required   # 👈 protege a rota
def editar_entrada(id):
    entrada = Financeiro.query.get_or_404(id)
    if entrada.tipo != "Entrada":
        flash("Registro inválido para edição.", "danger")
        return redirect(url_for('financeiro.entradas'))

    form = EntradaForm(obj=entrada)
    if form.validate_on_submit():
        entrada.categoria = form.tipo_receita.data
        entrada.valor = float(str(form.valor.data).replace(',', '.'))
        entrada.data = form.data.data
        entrada.descricao = form.descricao.data
        entrada.conta = form.conta.data
        db.session.commit()
        flash("Entrada atualizada com sucesso!", "success")
        return redirect(url_for('financeiro.entradas'))

    return render_template('financeiro/editar_entrada.html', form=form, entrada=entrada)

# -----------------------------
# 📄 Rotas de Saídas
# -----------------------------
@financeiro_bp.route('/saidas', methods=['GET', 'POST'])
@login_required   # 👈 protege a rota
def saidas():
    form = SaidaForm()
    if form.validate_on_submit():
        raw_valor = request.form.get('valor', '')
        valor_float = float(str(raw_valor).replace(',', '.'))

        nova = Financeiro(
            tipo="Saída",
            categoria=form.categoria.data,
            valor=valor_float,
            data=form.data.data,
            descricao=form.descricao.data,
            conta=form.conta.data
        )
        db.session.add(nova)
        db.session.commit()
        flash("Saída registrada com sucesso!", "success")
        return redirect(url_for('financeiro.saidas'))

    registros = Financeiro.query.filter_by(tipo="Saída").order_by(Financeiro.data.desc()).all()
    return render_template('financeiro/saidas.html', form=form, saidas=registros)

@financeiro_bp.route('/saidas/excluir/<int:id>', methods=['POST'])
@login_required   # 👈 protege a rota
def excluir_saida(id):
    saida = Financeiro.query.get_or_404(id)
    if saida.tipo != "Saída":
        flash("Registro inválido para exclusão.", "danger")
        return redirect(url_for('financeiro.saidas'))

    try:
        db.session.delete(saida)
        db.session.commit()
        flash("Saída excluída com sucesso!", "success")
    except Exception:
        db.session.rollback()
        flash("Erro ao excluir saída.", "danger")

    return redirect(url_for('financeiro.saidas'))

# ➡️ Nova rota para editar Saída
@financeiro_bp.route('/saidas/editar/<int:id>', methods=['GET', 'POST'])
@login_required   # 👈 protege a rota
def editar_saida(id):
    saida = Financeiro.query.get_or_404(id)
    if saida.tipo != "Saída":
        flash("Registro inválido para edição.", "danger")
        return redirect(url_for('financeiro.saidas'))

    form = SaidaForm(obj=saida)
    if form.validate_on_submit():
        saida.categoria = form.categoria.data
        saida.valor = float(str(form.valor.data).replace(',', '.'))
        saida.data = form.data.data
        saida.descricao = form.descricao.data
        saida.conta = form.conta.data
        db.session.commit()
        flash("Saída atualizada com sucesso!", "success")
        return redirect(url_for('financeiro.saidas'))

    return render_template('financeiro/editar_saida.html', form=form, saida=saida)

# -----------------------------
# 📄 Rotas de Relatórios, Exportação e Comprovantes
# -----------------------------
from flask_login import login_required   # 👈 protege rotas com Flask-Login

@financeiro_bp.route('/relatorios', methods=['GET', 'POST'])
@login_required   # 👈 protege a rota
def relatorios():
    form = FiltroRelatorioForm()
    query = Financeiro.query

    if form.validate_on_submit():
        if form.inicio.data:
            query = query.filter(Financeiro.data >= form.inicio.data)
        if form.fim.data:
            query = query.filter(Financeiro.data <= form.fim.data)
        if form.tipo.data:
            query = query.filter(Financeiro.tipo == form.tipo.data)
        if form.categoria.data:
            query = query.filter(Financeiro.categoria.ilike(f"%{form.categoria.data}%"))

    registros = query.order_by(Financeiro.data.desc()).all()

    total = sum(r.valor for r in registros)
    total_entradas = sum(r.valor for r in registros if r.tipo == "Entrada")
    total_saidas = sum(r.valor for r in registros if r.tipo == "Saída")

    # Agrupar por categoria para gráfico de pizza
    por_categoria = defaultdict(float)
    for r in registros:
        por_categoria[r.categoria] += float(r.valor)

    categorias_labels = list(por_categoria.keys())
    categorias_data = [por_categoria[c] for c in categorias_labels]

    return render_template(
        'financeiro/relatorios.html',
        form=form,
        registros=registros,
        total=total,
        total_entradas=total_entradas,
        total_saidas=total_saidas,
        categorias_labels=categorias_labels,
        categorias_data=categorias_data
    )

@financeiro_bp.route('/export.csv')
@login_required   # 👈 protege a rota
def export_csv():
    inicio_str = request.args.get('inicio')
    fim_str = request.args.get('fim')
    tipo = request.args.get('tipo')
    categoria = request.args.get('categoria')

    query = Financeiro.query
    def parse_date(s):
        return datetime.strptime(s, "%d-%m-%Y").date()

    if inicio_str:
        query = query.filter(Financeiro.data >= parse_date(inicio_str))
    if fim_str:
        query = query.filter(Financeiro.data <= parse_date(fim_str))
    if tipo:
        query = query.filter(Financeiro.tipo == tipo)
    if categoria:
        query = query.filter(Financeiro.categoria.ilike(f"%{categoria}%"))

    registros = query.order_by(Financeiro.data.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(["Data", "Tipo", "Categoria", "Conta", "Descrição", "Valor", "CPF Membro", "CNPJ Fornecedor", "Conciliado"])
    for r in registros:
        writer.writerow([
            r.data.strftime("%d-%m-%Y"),
            r.tipo,
            r.categoria,
            r.conta,
            r.descricao or "",
            f"{r.valor:.2f}",
            r.cpf_membro or "",
            r.cnpj_fornecedor or "",
            "Sim" if r.conciliado else "Não"
        ])

    return Response(output.getvalue(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment; filename=relatorio_financeiro.csv"})

@financeiro_bp.route('/comprovantes', methods=['GET', 'POST'])
@login_required   # 👈 protege a rota
def comprovantes():
    form = ComprovanteForm()
    if form.validate_on_submit():
        filename = secure_filename(form.arquivo.data.filename)
        destino = os.path.join(current_app.config['UPLOAD_FOLDER'], 'comprovantes')
        os.makedirs(destino, exist_ok=True)
        filepath = os.path.join(destino, filename)
        form.arquivo.data.save(filepath)

        novo = Financeiro(
            tipo="Comprovante",
            categoria="Upload",
            valor=0.0,
            data=form.data.data,
            descricao=form.descricao.data,
            comprovante=filename
        )
        db.session.add(novo)
        db.session.commit()
        flash("Comprovante enviado com sucesso!", "success")
        return redirect(url_for('financeiro.comprovantes'))

    registros = Financeiro.query.filter_by(tipo="Comprovante").order_by(Financeiro.data.desc()).all()
    por_mes = defaultdict(list)
    for r in registros:
        chave = r.data.strftime("%m-%Y")
        por_mes[chave].append(r)

    return render_template('financeiro/comprovantes.html', form=form, por_mes=por_mes)
