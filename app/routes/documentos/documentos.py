from flask import Blueprint, render_template, redirect, url_for, request, flash
from app import db
from app.models import Documento
from app.routes.documentos.forms import AtaForm   # importa o formulário
from datetime import date

documentos_bp = Blueprint("documentos", __name__, url_prefix="/documentos")

# -------------------
# Atas
# -------------------
@documentos_bp.route("/atas")
def listar_atas():
    page = request.args.get("page", 1, type=int)
    termo = request.args.get("q", "", type=str)

    query = Documento.query.filter(Documento.tipo.isnot(None))

    if termo:
        query = query.filter(
            (Documento.titulo.ilike(f"%{termo}%")) |
            (Documento.presidente.ilike(f"%{termo}%")) |
            (Documento.secretario.ilike(f"%{termo}%"))
        )

    atas = query.order_by(Documento.data.desc()).paginate(page=page, per_page=10)

    return render_template("documentos/atas.html", atas=atas, termo=termo)
    

# -----------------------------
# 🔍 Buscar Atas com paginação
# -----------------------------
@documentos_bp.route("/buscar", methods=["GET"])
def buscar_atas():
    termo = request.args.get("q", "").strip().lower()
    page = request.args.get("page", 1, type=int)

    query = Documento.query.filter(Documento.tipo.isnot(None))

    if termo:
        query = query.filter(
            (Documento.titulo.ilike(f"%{termo}%")) |
            (Documento.presidente.ilike(f"%{termo}%")) |
            (Documento.secretario.ilike(f"%{termo}%"))
        )

    atas = query.order_by(Documento.data.desc()).paginate(page=page, per_page=10)

    # 🔹 Só mostra mensagem se realmente houve busca
    if termo:
        if atas.total == 0:
            flash("Nenhuma ata corresponde ao termo pesquisado", "warning")
        elif atas.total == 1:
            flash("1 ata encontrada", "info")
        else:
            flash(f"{atas.total} atas encontradas", "info")

    return render_template("documentos/atas.html", atas=atas, termo=termo)

    
# ------------------- 
# Nova Ata
# -------------------
@documentos_bp.route("/atas/nova", methods=["GET", "POST"])
def nova_ata():
    form = AtaForm()
    if form.validate_on_submit():
        # Garante que data seja salva como date
        data_reuniao = form.data_reuniao.data
        if hasattr(data_reuniao, "date"):
            data_reuniao = data_reuniao.date()

        ata = Documento(
            titulo=form.titulo.data,
            tipo=form.tipo.data,
            situacao=form.situacao.data,
            data=data_reuniao,
            local=form.local.data,
            presidente=form.presidente.data,
            secretario=form.secretario.data,
            participantes=form.participantes.data,
            pauta=form.pauta.data,
            deliberacoes=form.deliberacoes.data,
            observacoes=form.observacoes.data,
            descricao=form.pauta.data,
            arquivo=None,
            criado_por=form.presidente.data
        )
        db.session.add(ata)
        db.session.commit()
        return redirect(url_for("documentos.listar_atas"))

    return render_template("documentos/nova_ata.html", form=form)

@documentos_bp.route("/atas/<int:id>")
def ver_ata(id):
    ata = Documento.query.get_or_404(id)
    return render_template("documentos/ver_ata.html", ata=ata)
    
# ------------------- 
# Editar Ata 
# -------------------
@documentos_bp.route("/atas/<int:id>/editar", methods=["GET", "POST"])
def editar_ata(id):
    ata = Documento.query.get_or_404(id)

    # Se a data estiver como datetime, converte para date
    if ata.data and hasattr(ata.data, "date"):
        ata.data = ata.data.date()

    form = AtaForm(obj=ata)  # pré-carrega os dados no formulário

    # 👇 Só força o preenchimento no GET (quando abre a página)
    if request.method == "GET":
        form.data_reuniao.data = ata.data

    if form.validate_on_submit():
        ata.titulo = form.titulo.data
        ata.tipo = form.tipo.data
        ata.situacao = form.situacao.data

        # Garante que data seja salva como date
        data_reuniao = form.data_reuniao.data
        if hasattr(data_reuniao, "date"):
            data_reuniao = data_reuniao.date()
        ata.data = data_reuniao

        ata.local = form.local.data
        ata.presidente = form.presidente.data
        ata.secretario = form.secretario.data
        ata.participantes = form.participantes.data
        ata.pauta = form.pauta.data
        ata.deliberacoes = form.deliberacoes.data
        ata.observacoes = form.observacoes.data

        db.session.commit()
        return redirect(url_for("documentos.listar_atas"))

    return render_template("documentos/editar_ata.html", form=form, ata=ata)

    
# ------------------- 
# Excluir Ata 
# -------------------
@documentos_bp.route("/atas/<int:id>/excluir", methods=["POST", "GET"])
def excluir_ata(id):
    ata = Documento.query.get_or_404(id)
    db.session.delete(ata)
    db.session.commit()
    return redirect(url_for("documentos.listar_atas"))
    

# -------------------
# Certificados
# -------------------
@documentos_bp.route("/certificados")
def listar_certificados():
    certificados = Documento.query.filter_by(tipo="certificado").order_by(Documento.data.desc()).all()
    return render_template("documentos/certificados.html", certificados=certificados)

# -------------------
# Cartas
# -------------------
@documentos_bp.route("/cartas")
def listar_cartas():
    cartas = Documento.query.filter_by(tipo="carta").order_by(Documento.data.desc()).all()
    return render_template("documentos/cartas.html", cartas=cartas)
