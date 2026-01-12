from flask import Blueprint, render_template, redirect, url_for, request, flash
from app import db
from app.models import Ata   # ✅ agora usamos o modelo Ata
from .forms import AtaForm
from datetime import date
from app.models.log import Log
from datetime import datetime, timezone
from flask import request
from app.extensions import db

atas_bp = Blueprint("atas", __name__, url_prefix="/atas")

def registrar_log(usuario, tarefa, resultado="sucesso"):
    """
    Registra um log no banco de dados.
    - usuario: e-mail ou identificador do usuário
    - tarefa: ação realizada (ex: login, logout, reset de senha)
    - resultado: 'sucesso', 'erro', 'info', etc.
    """
    try:
        log = Log(
            usuario=usuario,
            tarefa=tarefa,
            resultado=resultado,
            datahora=datetime.now(timezone.utc),
            ip=request.remote_addr or "desconhecido"
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao registrar log: {e}")

# ----------------------------- 
# 📋 Listar atas com paginação 
# -----------------------------
@atas_bp.route("/")
def listar_atas():
    page = request.args.get("page", 1, type=int)
    termo = request.args.get("q", "", type=str)

    query = Ata.query

    if termo:
        query = query.filter(
            (Ata.titulo.ilike(f"%{termo}%")) |
            (Ata.presidente.ilike(f"%{termo}%")) |
            (Ata.secretario.ilike(f"%{termo}%"))
        )

    atas = query.order_by(Ata.data_emissao.desc()).paginate(page=page, per_page=10)
    return render_template("documentos/atas/atas.html", atas=atas, termo=termo)

@atas_bp.route("/buscar", methods=["GET"])
def buscar_atas():
    termo = request.args.get("q", "").strip().lower()
    page = request.args.get("page", 1, type=int)

    query = Ata.query

    if termo:
        query = query.filter(
            (Ata.titulo.ilike(f"%{termo}%")) |
            (Ata.presidente.ilike(f"%{termo}%")) |
            (Ata.secretario.ilike(f"%{termo}%"))
        )

    atas = query.order_by(Ata.data_emissao.desc()).paginate(page=page, per_page=10)

    if termo:
        if atas.total == 0:
            flash("Nenhuma ata corresponde ao termo pesquisado", "warning")
        elif atas.total == 1:
            flash("1 ata encontrada", "info")
        else:
            flash(f"{atas.total} atas encontradas", "info")

    return render_template("documentos/atas/atas.html", atas=atas, termo=termo)


# ----------------------------- 
# 📝 Criar nova ata 
# -----------------------------
@atas_bp.route("/nova", methods=["GET", "POST"])
def nova_ata():
    form = AtaForm()
    if form.validate_on_submit():
        data_reuniao = form.data_reuniao.data
        if hasattr(data_reuniao, "date"):
            data_reuniao = data_reuniao.date()

        ata = Ata(
            titulo=form.titulo.data,
            data_emissao=data_reuniao,
            tipo=form.tipo.data,          # ✅ agora salva o tipo escolhido
            situacao=form.situacao.data,  # ✅ agora salva a situação escolhida
            local=form.local.data,
            presidente=form.presidente.data,
            secretario=form.secretario.data,
            participantes=form.participantes.data,
            pauta=form.pauta.data,
            deliberacoes=form.deliberacoes.data,
            observacoes=form.observacoes.data
        )
        db.session.add(ata)
        db.session.commit()

        # 🔹 Mensagem flash
        flash(f"Ata {ata.titulo} criada com sucesso!", "success")

        # 🔹 Log
        registrar_log(usuario=form.presidente.data or "desconhecido", tarefa=f"Criar Ata: {ata.titulo}")

        return redirect(url_for("documentos.atas.listar_atas"))

    return render_template("documentos/atas/nova_ata.html", form=form)

@atas_bp.route("/<int:id>")
def ver_ata(id):
    ata = Ata.query.get_or_404(id)
    return render_template("documentos/atas/ver_ata.html", ata=ata)
    
    
# ----------------------------- 
# ✏️ Editar ata existente 
# -----------------------------
@atas_bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar_ata(id):
    ata = Ata.query.get_or_404(id)
    if ata.data_emissao and hasattr(ata.data_emissao, "date"):
        ata.data_emissao = ata.data_emissao.date()

    form = AtaForm(obj=ata)
    if request.method == "GET":
        form.data_reuniao.data = ata.data_emissao

    if form.validate_on_submit():
        ata.titulo = form.titulo.data
        data_reuniao = form.data_reuniao.data
        if hasattr(data_reuniao, "date"):
            data_reuniao = data_reuniao.date()
        ata.data_emissao = data_reuniao
        ata.tipo = form.tipo.data         # ✅ atualiza tipo
        ata.situacao = form.situacao.data # ✅ atualiza situação
        ata.local = form.local.data
        ata.presidente = form.presidente.data
        ata.secretario = form.secretario.data
        ata.participantes = form.participantes.data
        ata.pauta = form.pauta.data
        ata.deliberacoes = form.deliberacoes.data
        ata.observacoes = form.observacoes.data
        db.session.commit()

        # 🔹 Mensagem flash
        flash(f"Ata {ata.titulo} atualizada com sucesso!", "info")

        # 🔹 Log
        registrar_log(usuario=form.presidente.data or "desconhecido", tarefa=f"Editar Ata: {ata.titulo}")

        return redirect(url_for("documentos.atas.listar_atas"))

    return render_template("documentos/atas/editar_ata.html", form=form, ata=ata)


# ----------------------------- 
# 🗑️ Excluir ata existente 
# -----------------------------
@atas_bp.route("/<int:id>/excluir", methods=["POST", "GET"])
def excluir_ata(id):
    ata = Ata.query.get_or_404(id)
    db.session.delete(ata)
    db.session.commit()

    # 🔹 Mensagem flash
    flash(f"Ata {ata.titulo} excluída com sucesso!", "danger")

    # 🔹 Log
    registrar_log(usuario=ata.presidente or "desconhecido", tarefa=f"Excluir Ata: {ata.titulo}")

    return redirect(url_for("documentos.atas.listar_atas"))
