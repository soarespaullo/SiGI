from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import User
from functools import wraps
from .forms import NovoUsuarioForm, EditarUsuarioForm
from utils.logs import registrar_log
import os

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

# Pasta de upload dentro de app/static/uploads
def get_upload_folder():
    return os.path.join(current_app.root_path, "static", "uploads")

# Decorator para garantir acesso apenas a administradores
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@usuarios_bp.route("/")
@admin_required
def usuarios_page():
    usuarios = User.query.all()
    return render_template("configuracoes/usuarios.html", usuarios=usuarios)

@usuarios_bp.route("/novo", methods=["GET", "POST"])
@admin_required
def novo_usuario():
    form = NovoUsuarioForm()
    if form.validate_on_submit():
        novo = User(
            nome=form.nome.data,
            email=form.email.data,
            role=form.role.data,
            ativo=(form.ativo.data == "true")
        )
        novo.set_password(form.senha.data)

        # Primeiro commit para gerar o ID
        db.session.add(novo)
        db.session.commit()

        # Foto (se enviada)
        if form.foto.data:
            foto = form.foto.data
            ext = os.path.splitext(foto.filename)[1].lower()
            if ext not in [".jpg", ".jpeg", ".png"]:
                flash("Formato inválido. Use JPG ou PNG.", "danger")
            else:
                filename = secure_filename(f"user_{novo.id}{ext}")
                upload_folder = get_upload_folder()
                os.makedirs(upload_folder, exist_ok=True)
                path = os.path.join(upload_folder, filename)
                foto.save(path)
                novo.foto = filename
                db.session.commit()  # segundo commit para atualizar a foto

        registrar_log(current_user.nome, f"Criou usuário: {novo.email}", "sucesso")
        flash("Usuário criado com sucesso!", "success")
        return redirect(url_for("configuracoes.usuarios.usuarios_page"))
    return render_template("configuracoes/novo_usuario.html", form=form)

@usuarios_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@admin_required
def editar_usuario(id):
    usuario = User.query.get_or_404(id)
    form = EditarUsuarioForm(obj=usuario)
    if request.method == "GET":
        form.ativo.data = "true" if usuario.ativo else "false"

    if form.validate_on_submit():
        usuario.nome = form.nome.data
        usuario.email = form.email.data
        usuario.role = form.role.data
        usuario.ativo = (form.ativo.data == "true")
        if form.senha.data:
            usuario.set_password(form.senha.data)

        # Foto (se enviada)
        if form.foto.data:
            foto = form.foto.data
            ext = os.path.splitext(foto.filename)[1].lower()
            if ext not in [".jpg", ".jpeg", ".png"]:
                flash("Formato inválido. Use JPG ou PNG.", "danger")
            else:
                upload_folder = get_upload_folder()
                os.makedirs(upload_folder, exist_ok=True)

                # Remove foto antiga se existir
                if usuario.foto:
                    old_path = os.path.join(upload_folder, usuario.foto)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                filename = secure_filename(f"user_{usuario.id}{ext}")
                path = os.path.join(upload_folder, filename)
                foto.save(path)
                usuario.foto = filename

        db.session.commit()
        registrar_log(current_user.nome, f"Editou usuário: {usuario.email}", "sucesso")
        flash("Usuário atualizado com sucesso!", "success")
        return redirect(url_for("configuracoes.usuarios.usuarios_page"))
    return render_template("configuracoes/editar_usuario.html", form=form, usuario=usuario)

@usuarios_bp.route("/<int:id>/excluir", methods=["POST"])
@admin_required
def excluir_usuario(id):
    usuario = User.query.get_or_404(id)

    # 🔹 Remove foto física se existir
    if usuario.foto:
        upload_folder = get_upload_folder()
        path = os.path.join(upload_folder, usuario.foto)
        if os.path.exists(path):
            os.remove(path)

    db.session.delete(usuario)
    db.session.commit()

    registrar_log(current_user.nome, f"Excluiu usuário: {usuario.email}", "sucesso")
    flash("Usuário excluído com sucesso!", "success")
    return redirect(url_for("configuracoes.usuarios.usuarios_page"))

@usuarios_bp.route("/<int:id>/toggle", methods=["POST"])
@admin_required
def toggle_usuario(id):
    usuario = User.query.get_or_404(id)
    usuario.ativo = not usuario.ativo
    db.session.commit()
    registrar_log(current_user.nome, f"Trocou status do usuário: {usuario.email} para {'ativo' if usuario.ativo else 'inativo'}", "sucesso")
    flash(
        f"Usuário {usuario.nome} foi {'ativado' if usuario.ativo else 'desativado'}.",
        "success" if usuario.ativo else "warning"
    )
    return redirect(url_for("configuracoes.usuarios.usuarios_page"))

@usuarios_bp.route("/<int:id>/remover_foto", methods=["POST"])
@admin_required
def remover_foto(id):
    usuario = User.query.get_or_404(id)

    if usuario.foto:
        upload_folder = get_upload_folder()
        path = os.path.join(upload_folder, usuario.foto)

        # Remove arquivo físico
        if os.path.exists(path):
            os.remove(path)

        # Limpa campo no banco
        usuario.foto = None
        db.session.commit()

        registrar_log(current_user.nome, f"Removeu foto do usuário: {usuario.email}", "sucesso")
        flash("Foto removida com sucesso!", "info")
    else:
        flash("Este usuário não possui foto cadastrada.", "warning")

    return redirect(url_for("configuracoes.usuarios.editar_usuario", id=id))
