import os
from datetime import datetime, date
from collections import Counter

from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, current_app, make_response, Response
)
from flask_login import login_required
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
from sqlalchemy import func
from weasyprint import HTML  # ➕ para gerar PDF

from utils.pagination import paginate_query
from app.models import Member, PublicLink   # 👈 importa os modelos
from app.routes.member.forms import MemberForm   # 👈 importa o formulário do lugar certo
from app.extensions import db


member_bp = Blueprint('member', __name__, url_prefix="/membros")

# -----------------------------
# 📋 Listagem de Membros com Paginação (ajustada para link visitante)
# -----------------------------
@member_bp.route("/", methods=["GET"])
@login_required   # 👈 protege a rota
def listar_membros():
    page = request.args.get("page", 1, type=int)
    termo = request.args.get("q", "")   # 🔹 captura termo de busca

    membros = Member.query.order_by(Member.nome.asc()).paginate(page=page, per_page=10)

    # 🔹 Busca o último link de visitante ativo
    visitante_link = PublicLink.query.filter_by(tipo="visitante", ativo=True).order_by(PublicLink.data_criacao.desc()).first()

    # Se não existir, cria um novo
    if not visitante_link:
        novo_hash = PublicLink.gerar_hash()
        visitante_link = PublicLink(tipo="visitante", hash=novo_hash)
        db.session.add(visitante_link)
        db.session.commit()

    # Monta a URL pública
    visitante_link_url = url_for("member.cadastro_visitante", hash=visitante_link.hash, _external=True)

    return render_template(
        "membros/listar_membros.html",
        membros=membros,
        visitante_link_url=visitante_link_url,
        termo=termo   # 🔹 passa termo para o template
    )


# -----------------------------
# 🔍 Buscar Membros
# -----------------------------
@member_bp.route("/buscar", methods=["GET"])
@login_required   # 👈 protege a rota
def buscar_membros():
    termo = request.args.get("q", "").strip().lower()
    page = request.args.get("page", 1, type=int)

    query = Member.query
    if termo:
        query = query.filter(
            (Member.nome.ilike(f"%{termo}%")) |
            (Member.email.ilike(f"%{termo}%")) |
            (Member.funcao.ilike(f"%{termo}%"))
        )

    query = query.order_by(Member.nome.asc())
    membros = query.paginate(page=page, per_page=10)

    if termo:
        if membros.total == 0:
            flash("Nenhum membro encontrado", "warning")
        elif membros.total == 1:
            flash("1 membro encontrado", "info")
        else:
            flash(f"{membros.total} membro(s) encontrado(s)", "info")

    return render_template("membros/listar_membros.html", membros=membros, termo=termo)

# -----------------------------
# ➕ Cadastro de Membros
# -----------------------------
@member_bp.route("/cadastro", methods=["GET", "POST"])
@login_required   # 👈 protege a rota
def cadastro_membro():
    form = MemberForm(CombinedMultiDict([request.form, request.files]))
    if request.method == "POST" and form.validate_on_submit():
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
@login_required   # 👈 protege a rota
def editar_membro(id):
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
@login_required   # 👈 protege a rota
def excluir_membro(id):
    membro = Member.query.get_or_404(id)
    db.session.delete(membro)
    db.session.commit()
    flash("Membro excluído com sucesso!", "info")
    return redirect(url_for("member.listar_membros"))


# -----------------------------
# 🎂 Aniversariantes do Mês
# -----------------------------
@member_bp.route("/aniversariantes", methods=["GET"])
@login_required
def aniversariantes_mes():
    # Captura filtros
    mes = request.args.get("mes", type=int)
    funcao = request.args.get("funcao")
    dia_inicio = request.args.get("dia_inicio", type=int)
    dia_fim = request.args.get("dia_fim", type=int)
    page = request.args.get("page", 1, type=int)

    # Se não passar mês, usa o mês atual
    if not mes:
        mes = datetime.now().month

    # Query base
    query = Member.query.filter(Member.data_nascimento.isnot(None))
    query = query.filter(func.extract('month', Member.data_nascimento) == mes)

    if funcao:
        query = query.filter(Member.funcao == funcao)
    if dia_inicio and dia_fim:
        query = query.filter(func.extract('day', Member.data_nascimento).between(dia_inicio, dia_fim))

    # 🔹 Paginação: ajuste o parâmetro `per_page` para definir quantos membros aparecem por página.
    # Exemplo: per_page=12 → só aparece paginação se houver mais de 12 membros.
    aniversariantes = query.order_by(func.extract('day', Member.data_nascimento)).paginate(page=page, per_page=12)

    meses = [
        "Janeiro","Fevereiro","Março","Abril","Maio","Junho",
        "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"
    ]

    funcoes = [f[0] for f in db.session.query(Member.funcao).distinct().all()]

    return render_template(
        "membros/aniversariantes_mes.html",
        aniversariantes=aniversariantes,
        meses=meses,
        mes_atual=meses[mes - 1],
        mes_selecionado=mes,
        funcoes=funcoes,
        funcao_selecionada=funcao,
        dia_inicio=dia_inicio,
        dia_fim=dia_fim,
        current_year=datetime.now().year
    )


# -----------------------------
# 🪪 Carteira de Membro (HTML)
# -----------------------------
@member_bp.route("/carteira/<int:id>", methods=["GET"])
@login_required   # 👈 protege a rota
def carteira_membro(id):
    membro = Member.query.get_or_404(id)
    return render_template("membros/carteira_modelo.html", membro=membro)

# -----------------------------
# 📄 Carta de Recomendação (HTML + PDF)
# -----------------------------
@member_bp.route("/carta_recomendacao/<int:id>", methods=["GET"])
@login_required   # 👈 protege a rota
def carta_recomendacao(id):
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
@login_required   # 👈 protege a rota
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
@login_required   # 👈 protege a rota
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
@login_required   # 👈 protege a rota
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
    # Gera o PDF com WeasyPrint
    pdf = HTML(string=html).write_pdf()

    return Response(
        pdf,
        mimetype="application/pdf",
        headers={"Content-Disposition": "inline; filename=relatorio_membros.pdf"}
    )

# -----------------------------
# 🌐 Cadastro público de visitante
# -----------------------------
from sqlalchemy import or_, and_

@member_bp.route("/cadastro-visitante/<hash>", methods=["GET", "POST"])
def cadastro_visitante(hash):
    # ✅ valida se a hash existe e está ativa para tipo "visitante"
    link = PublicLink.query.filter_by(hash=hash, ativo=True, tipo="visitante").first_or_404()

    form = MemberForm()  # 👈 instancia o FlaskForm

    if request.method == "POST":
        nome = request.form.get("nome")
        telefone = request.form.get("telefone")
        email = request.form.get("email")
        data_nascimento_str = request.form.get("data_nascimento")
        sexo = request.form.get("sexo")
        estado_civil = request.form.get("estado_civil")
        conjuge = request.form.get("conjuge") if estado_civil == "Casado" else None
        frequenta = request.form.get("frequenta")
        endereco = request.form.get("endereco")
        bairro = request.form.get("bairro")
        naturalidade = request.form.get("naturalidade")   # 👈 ainda pega do form
        cep = request.form.get("cep")
        observacoes = request.form.get("observacoes")

        # 🔒 Converte data de nascimento para objeto date (compatível MySQL/SQLite)
        data_nascimento = None
        if data_nascimento_str:
            try:
                data_nascimento = datetime.strptime(data_nascimento_str, "%Y-%m-%d").date()
            except ValueError:
                data_nascimento = None

        # 🔒 Validação obrigatória
        if not nome or not telefone:
            flash("Nome e Telefone são obrigatórios!", "danger")
            return redirect(url_for("member.cadastro_visitante", hash=hash))

        # 🚫 Verifica duplicidade (mesmo nome+telefone OU mesmo email)
        conditions = [
            and_(Member.nome == nome, Member.telefone == telefone)
        ]
        if email:  # só verifica email se informado
            conditions.append(Member.email == email)

        existente = Member.query.filter(or_(*conditions)).first()

        if existente:
            flash("Este visitante já está cadastrado no sistema!", "warning")
            return redirect(url_for("member.cadastro_visitante", hash=hash))

        # ✅ Se não existe, cria novo visitante
        visitante = Member(
            nome=nome,
            telefone=telefone,
            email=email,
            data_nascimento=data_nascimento,
            sexo=sexo,
            estado_civil=estado_civil,
            conjuge=conjuge,
            endereco=endereco,
            bairro=bairro,
            naturalidade=naturalidade,  # 👈 ajuste: salva em naturalidade
            cep=cep,
            observacoes=observacoes,
            funcao="Visitante",          # 👈 marca como visitante
            status="Ativo",              # 👈 status padrão
            data_cadastro=datetime.utcnow()
        )
        db.session.add(visitante)
        db.session.commit()

        # 👉 após cadastrar, renderiza a tela de sucesso
        return render_template("membros/success.html", visitante=visitante, hash=hash)

    # ✅ se GET, renderiza o formulário estilizado e passa o form + hash
    return render_template("membros/cadastro_visitante.html", form=form, hash=hash)
    
    
# -----------------------------
# 📄 Relatório em PDF de Aniversariantes
# -----------------------------
@member_bp.route("/membros/aniversariantes/pdf", methods=["GET"])
@login_required
def exportar_aniversariantes_pdf():
    # 🔹 Captura filtros da URL
    mes = request.args.get("mes", type=int)
    funcao = request.args.get("funcao")
    dia_inicio = request.args.get("dia_inicio", type=int)
    dia_fim = request.args.get("dia_fim", type=int)

    # 🔹 Se não for passado mês, usa o mês atual
    if not mes:
        mes = datetime.now().month

    # 🔹 Filtros diretos
    query = Member.query.filter(Member.data_nascimento.isnot(None))
    query = query.filter(func.extract('month', Member.data_nascimento) == mes)

    if funcao:
        query = query.filter(Member.funcao == funcao)
    if dia_inicio and dia_fim:
        query = query.filter(
            func.extract('day', Member.data_nascimento).between(dia_inicio, dia_fim)
        )

    aniversariantes = query.order_by(Member.data_nascimento).all()

    # 🔹 Data de emissão (somente dia/mês/ano)
    data_emissao = datetime.now().strftime("%d/%m/%Y")

    # 🔹 Renderiza template PDF
    html = render_template(
        "membros/aniversariantes_pdf.html",
        aniversariantes=aniversariantes,
        current_year=datetime.now().year,
        data_emissao=data_emissao
    )

    pdf = HTML(string=html).write_pdf()
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=aniversariantes.pdf"
    return response

