from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User
from functools import wraps
from .forms import NovoUsuarioForm, EditarUsuarioForm  # ajuste conforme seu path
from utils.logs import registrar_log   # 👈 importa função de log

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

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
    return render_template("admin/usuarios.html", usuarios=usuarios)

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
        db.session.add(novo)
        db.session.commit()
        registrar_log(current_user.nome, f"Criou usuário: {novo.email}", "sucesso")  # 👈 log
        flash("Usuário criado com sucesso!", "success")
        return redirect(url_for("admin.usuarios.usuarios_page"))
    return render_template("admin/novo_usuario.html", form=form)

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
        db.session.commit()
        registrar_log(current_user.nome, f"Editou usuário: {usuario.email}", "sucesso")  # 👈 log
        flash("Usuário atualizado com sucesso!", "success")
        return redirect(url_for("admin.usuarios.usuarios_page"))
    return render_template("admin/editar_usuario.html", form=form, usuario=usuario)

@usuarios_bp.route("/<int:id>/excluir", methods=["POST"])
@admin_required
def excluir_usuario(id):
    usuario = User.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    registrar_log(current_user.nome, f"Excluiu usuário: {usuario.email}", "sucesso")  # 👈 log
    flash("Usuário excluído com sucesso!", "success")
    return redirect(url_for("admin.usuarios.usuarios_page"))

@usuarios_bp.route("/<int:id>/toggle", methods=["POST"])
@admin_required
def toggle_usuario(id):
    usuario = User.query.get_or_404(id)
    usuario.ativo = not usuario.ativo
    db.session.commit()
    registrar_log(current_user.nome, f"Trocou status do usuário: {usuario.email} para {'ativo' if usuario.ativo else 'inativo'}", "sucesso")  # 👈 log
    flash(
        f"Usuário {usuario.nome} foi {'ativado' if usuario.ativo else 'desativado'}.",
        "success" if usuario.ativo else "warning"
    )
    return redirect(url_for("admin.usuarios.usuarios_page"))
