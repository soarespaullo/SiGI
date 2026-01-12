from flask import Blueprint, render_template, redirect, url_for, flash, request
from datetime import datetime
from app import db
from app.models import Certificado   # ✅ agora usamos o modelo Certificado
from .forms import CertificadoForm

certificados_bp = Blueprint("certificados", __name__, url_prefix="/certificados")

# -----------------------------
# 📋 Listar certificados com paginação e busca
# -----------------------------
@certificados_bp.route("/")
def listar_certificados():
    page = request.args.get("page", 1, type=int)   # página atual
    termo = request.args.get("q", "", type=str)    # termo de busca

    query = Certificado.query

    if termo:
        query = query.filter(
            (Certificado.titulo.ilike(f"%{termo}%")) |
            (Certificado.corpo.ilike(f"%{termo}%")) |
            (Certificado.criado_por.ilike(f"%{termo}%")) |
            (Certificado.evento.ilike(f"%{termo}%"))
        )

    certificados = query.order_by(Certificado.data_emissao.desc()).paginate(page=page, per_page=10)

    if termo:
        if certificados.total == 0:
            flash("Nenhum certificado corresponde ao termo pesquisado", "warning")
        elif certificados.total == 1:
            flash("1 certificado encontrado", "info")
        else:
            flash(f"{certificados.total} certificados encontrados", "info")

    return render_template(
        "documentos/certificados/certificados.html",
        certificados=certificados,
        termo=termo
    )


# -----------------------------
# 👁️ Visualizar certificado
# -----------------------------
@certificados_bp.route("/<int:id>")
def visualizar_certificado(id):
    certificado = Certificado.query.get_or_404(id)
    return render_template("documentos/certificados/certificado_detalhe.html", certificado=certificado)


# -----------------------------
# 📝 Criar novo certificado
# -----------------------------
@certificados_bp.route("/novo", methods=["GET", "POST"])
def novo_certificado():
    form = CertificadoForm()
    if form.validate_on_submit():
        certificado = Certificado(
            titulo=form.titulo.data,
            corpo=form.corpo.data,
            data_emissao=form.data_emissao.data or datetime.utcnow(),
            criado_por=form.criado_por.data,      # ✅ corrigido
            evento=form.evento.data,
            situacao=form.situacao.data           # ✅ agora salva situação
        )
        db.session.add(certificado)
        db.session.commit()
        flash(f"Certificado {certificado.titulo} criado com sucesso!", "success")
        return redirect(url_for("documentos.certificados.listar_certificados"))
    return render_template("documentos/certificados/certificado_novo.html", form=form)


# -----------------------------
# ✏️ Editar certificado existente
# -----------------------------
@certificados_bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar_certificado(id):
    certificado = Certificado.query.get_or_404(id)
    form = CertificadoForm(obj=certificado)

    if form.validate_on_submit():
        certificado.titulo = form.titulo.data
        certificado.corpo = form.corpo.data
        certificado.data_emissao = form.data_emissao.data or datetime.utcnow()
        certificado.criado_por = form.criado_por.data   # ✅ corrigido
        certificado.evento = form.evento.data
        certificado.situacao = form.situacao.data       # ✅ agora atualiza situação

        db.session.commit()
        flash(f"Certificado {certificado.titulo} atualizado com sucesso!", "info")
        return redirect(url_for("documentos.certificados.listar_certificados"))

    return render_template(
        "documentos/certificados/editar_certificado.html",
        form=form,
        certificado=certificado
    )


# -----------------------------
# 🗑️ Excluir certificado existente
# -----------------------------
@certificados_bp.route("/<int:id>/excluir", methods=["POST", "GET"])
def excluir_certificado(id):
    certificado = Certificado.query.get_or_404(id)
    titulo = certificado.titulo
    db.session.delete(certificado)
    db.session.commit()

    flash(f"Certificado {titulo} excluído com sucesso!", "danger")
    return redirect(url_for("documentos.certificados.listar_certificados"))
