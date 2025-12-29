from flask import Blueprint, render_template, redirect, url_for, session, flash, request, current_app, make_response, Response
from models import db, Member
from .forms import MemberForm
import os
import weasyprint 
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
from sqlalchemy import func
from datetime import datetime, date
from weasyprint import HTML  # ➕ para gerar PDF
from collections import Counter

member_bp = Blueprint('member', __name__, url_prefix="/membros")

# -----------------------------
# 📋 Listagem de Membros
# -----------------------------
@member_bp.route("/", methods=["GET"])
def listar_membros():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    membros = Member.query.order_by(Member.nome.asc()).all()
    return render_template("membros/listar_membros.html", membros=membros)

# -----------------------------
# 🔍 Buscar Membros
# -----------------------------
@member_bp.route("/buscar", methods=["GET"])
def buscar_membros():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    termo = request.args.get("q", "").strip().lower()
    if termo:
        membros = Member.query.filter(
            (Member.nome.ilike(f"%{termo}%")) |
            (Member.email.ilike(f"%{termo}%")) |
            (Member.funcao.ilike(f"%{termo}%"))
        ).order_by(Member.nome.asc()).all()
    else:
        membros = Member.query.order_by(Member.nome.asc()).all()

    if not membros:
        flash("Nenhum membro encontrado", "warning")
    elif len(membros) == 1:
        flash("1 membro encontrado", "info")
    else:
        flash(f"{len(membros)} membro(s) encontrado(s)", "info")

    return render_template("membros/listar_membros.html", membros=membros)

# -----------------------------
# ➕ Cadastro de Membros
# -----------------------------
@member_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro_membro():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    form = MemberForm(CombinedMultiDict([request.form, request.files]))
    if request.method == "POST" and form.validate_on_submit():
        # 🔒 Validação de duplicidade corrigida
        existente = None
        if form.cpf.data:
            existente = Member.query.filter(Member.cpf == form.cpf.data).first()
        elif form.nome.data and form.data_nascimento.data:
            existente = Member.query.filter(
                (Member.nome == form.nome.data) &
                (Member.data_nascimento == form.data_nascimento.data)
            ).first()

        if existente:
            flash("Já existe um membro cadastrado com esses dados!", "danger")
            return render_template("membros/cadastro_membro.html", form=form)

        membro = Member(
            nome=form.nome.data,
            data_nascimento=form.data_nascimento.data,
            sexo=form.sexo.data,
            estado_civil=form.estado_civil.data,
            conjuge=form.conjuge.data if form.estado_civil.data == "Casado" else None,
            telefone=form.telefone.data,
            email=form.email.data,
            endereco=form.endereco.data,
            bairro=form.bairro.data,
            cep=form.cep.data,
            batizado=form.batizado.data,
            dizimista=form.dizimista.data,
            data_batismo=form.data_batismo.data,
            funcao=form.funcao.data,
            observacoes=form.observacoes.data,
            status=form.status.data,
            nacionalidade=form.nacionalidade.data,
            naturalidade=form.naturalidade.data,
            rg=form.rg.data,
            cpf=form.cpf.data,
            pai=form.pai.data,
            mae=form.mae.data,
            filiacao=form.filiacao.data,
            numero_carteira=form.numero_carteira.data,
            igreja_local=form.igreja_local.data,
            validade=form.validade.data,
            data_cadastro=form.data_cadastro.data,
            data_conversao=form.data_conversao.data,
            data_saida=form.data_saida.data
        )

        foto_file = form.foto.data
        if foto_file:
            filename = secure_filename(foto_file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            foto_path = os.path.join(upload_folder, filename)
            foto_file.save(foto_path)
            membro.foto = f"uploads/{filename}"

        db.session.add(membro)
        db.session.commit()
        flash("Membro cadastrado com sucesso!", "success")
        return redirect(url_for("member.listar_membros"))

    return render_template("membros/cadastro_membro.html", form=form)

# -----------------------------
# ✏️ Edição de Membros
# -----------------------------
@member_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_membro(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    membro = Member.query.get_or_404(id)
    form = MemberForm(CombinedMultiDict([request.form, request.files]), obj=membro)

    if request.method == "GET":
        form.batizado.data = membro.batizado
        form.dizimista.data = membro.dizimista

    if request.method == "POST" and form.validate_on_submit():
        membro.nome = form.nome.data
        membro.data_nascimento = form.data_nascimento.data
        membro.sexo = form.sexo.data
        membro.estado_civil = form.estado_civil.data
        membro.conjuge = form.conjuge.data if form.estado_civil.data == "Casado" else None
        membro.telefone = form.telefone.data
        membro.email = form.email.data
        membro.endereco = form.endereco.data
        membro.bairro = form.bairro.data
        membro.cep = form.cep.data
        membro.batizado = form.batizado.data
        membro.dizimista = form.dizimista.data
        membro.data_batismo = form.data_batismo.data
        membro.funcao = form.funcao.data
        membro.observacoes = form.observacoes.data
        membro.status = form.status.data
        membro.nacionalidade = form.nacionalidade.data
        membro.naturalidade = form.naturalidade.data
        membro.rg = form.rg.data
        membro.cpf = form.cpf.data
        membro.pai = form.pai.data
        membro.mae = form.mae.data
        membro.filiacao = form.filiacao.data
        membro.numero_carteira = form.numero_carteira.data
        membro.igreja_local = form.igreja_local.data
        membro.validade = form.validade.data or membro.validade
        membro.data_cadastro = form.data_cadastro.data or membro.data_cadastro
        membro.data_conversao = form.data_conversao.data or membro.data_conversao
        membro.data_saida = form.data_saida.data or membro.data_saida

        foto_file = form.foto.data
        if foto_file:
            filename = secure_filename(foto_file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            foto_path = os.path.join(upload_folder, filename)
            foto_file.save(foto_path)
            membro.foto = f"uploads/{filename}"

        if "remover_foto" in request.form:
            membro.foto = None

        db.session.commit()
        flash("Membro atualizado com sucesso!", "success")
        return redirect(url_for("member.listar_membros"))

    return render_template("membros/editar_membro.html", form=form, membro=membro)

# -----------------------------
# ❌ Exclusão de Membros
# -----------------------------
@member_bp.route("/excluir/<int:id>", methods=["POST"])
def excluir_membro(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    membro = Member.query.get_or_404(id)
    db.session.delete(membro)
    db.session.commit()
    flash("Membro excluído com sucesso!", "info")
    return redirect(url_for("member.listar_membros"))

# -----------------------------
# 🎂 Aniversariantes do Mês
# -----------------------------
@member_bp.route("/aniversariantes", methods=["GET"])
def aniversariantes_mes():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    mes_atual = datetime.now().month
    aniversariantes = (
        Member.query
        .filter(func.extract('month', Member.data_nascimento) == mes_atual)
        .order_by(func.extract('day', Member.data_nascimento))
        .all()
    )

    return render_template(
        "membros/aniversariantes_mes.html",
        aniversariantes=aniversariantes,
        mes_atual=mes_atual
    )

# -----------------------------
# 🪪 Carteira de Membro (HTML)
# -----------------------------
@member_bp.route("/carteira/<int:id>", methods=["GET"])
def carteira_membro(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    membro = Member.query.get_or_404(id)
    return render_template("membros/carteira_modelo.html", membro=membro)

# -----------------------------
# 📄 Carta de Recomendação (HTML)
# -----------------------------
@member_bp.route("/carta_recomendacao/<int:id>", methods=["GET"])
def carta_recomendacao(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    membro = Member.query.get_or_404(id)

    html_string = render_template(
        "membros/carta_recomendacao.html",
        membro=membro,
        data_emissao=datetime.now().strftime("%d/%m/%Y")
    )
    pdf = HTML(string=html_string).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=carta_recomendacao_{membro.id}.pdf'
    return response

# -----------------------------
# 📄 Ficha de Membro (PDF)
# -----------------------------
@member_bp.route('/membro/<int:id>/ficha/pdf')
def imprimir_ficha_pdf(id):
    membro = Member.query.get_or_404(id)

    foto_url = None
    if membro.foto:
        foto_url = url_for('static', filename=membro.foto, _external=True)

    html = render_template(
        'membros/ficha_pdf.html',
        membro=membro,
        foto_url=foto_url,
        current_date=date.today()
    )
    pdf = HTML(string=html).write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=ficha_{membro.id}.pdf'
    return response

# -----------------------------
# 📊 Relatório de Membros
# -----------------------------
@member_bp.route("/relatorio", methods=["GET"])
def relatorio_membros():
    sexo = request.args.get("sexo")
    status = request.args.get("status")
    estado_civil = request.args.get("estado_civil")
    funcao = request.args.get("funcao")

    query = Member.query
    if sexo:
        query = query.filter(Member.sexo == sexo)
    if status:
        query = query.filter(Member.status == status)
    if estado_civil:
        query = query.filter(Member.estado_civil == estado_civil)
    if funcao:
        query = query.filter(Member.funcao == funcao)

    membros = query.all()

    dist_sexo_raw = (
        query.with_entities(Member.sexo, func.count(Member.id))
        .group_by(Member.sexo)
        .all()
    )
    dist_status_raw = (
        query.with_entities(Member.status, func.count(Member.id))
        .group_by(Member.status)
        .all()
    )
    dist_estado_civil_raw = (
        query.with_entities(Member.estado_civil, func.count(Member.id))
        .group_by(Member.estado_civil)
        .all()
    )
    dist_funcao_raw = (
        query.with_entities(Member.funcao, func.count(Member.id))
        .group_by(Member.funcao)
        .all()
    )

    dist_sexo = [((s or "Não informado"), int(c)) for s, c in dist_sexo_raw]
    dist_status = [((st or "Não informado"), int(c)) for st, c in dist_status_raw]
    dist_estado_civil = [((ec or "Não informado"), int(c)) for ec, c in dist_estado_civil_raw]
    dist_funcao = [((f or "Não informado"), int(c)) for f, c in dist_funcao_raw]

    def calcula_idade(nasc):
        if not nasc:
            return None
        hoje = date.today()
        return hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))

    faixas = []
    for m in membros:
        idade = calcula_idade(m.data_nascimento)
        if idade is None:
            continue
        if idade <= 18:
            faixas.append("0-18")
        elif idade <= 35:
            faixas.append("19-35")
        elif idade <= 60:
            faixas.append("36-60")
        else:
            faixas.append("60+")

    dist_idade = Counter(faixas)

    return render_template(
        "membros/relatorio_membros.html",
        membros=membros,
        dist_sexo=dist_sexo,
        dist_status=dist_status,
        dist_estado_civil=dist_estado_civil,
        dist_funcao=dist_funcao,
        dist_idade=dist_idade,
    )

# ----------------------------------------
# 📊 Relatório de Membros Estatísticos PDF
# -----------------------------------------
@member_bp.route("/relatorio/pdf")
def relatorio_membros_pdf():
    sexo = request.args.get("sexo")
    status = request.args.get("status")
    estado_civil = request.args.get("estado_civil")
    funcao = request.args.get("funcao")

    query = Member.query
    if sexo:
        query = query.filter(Member.sexo == sexo)
    if status:
        query = query.filter(Member.status == status)
    if estado_civil:
        query = query.filter(Member.estado_civil == estado_civil)
    if funcao:
        query = query.filter(Member.funcao == funcao)

    membros = query.all()

    html = render_template(
        "membros/relatorio_membros_pdf.html",
        membros=membros,
        sexo=sexo,
        status=status,
        estado_civil=estado_civil,
        funcao=funcao,
        data_emissao=date.today().strftime("%d/%m/%Y")
    )

    pdf = weasyprint.HTML(string=html).write_pdf()

    return Response(
        pdf,
        mimetype="application/pdf",
        headers={"Content-Disposition": "inline; filename=relatorio_membros.pdf"}
    )

