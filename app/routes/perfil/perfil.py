from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User
from .forms import EditarPerfilForm, AlterarSenhaForm
from utils.logs import registrar_log   # ✅ importar o logger

perfil_bp = Blueprint("perfil", __name__, url_prefix="/perfil")

@perfil_bp.route("/", methods=["GET", "POST"])
@login_required
def meu_perfil():
    form = AlterarSenhaForm()
    if form.validate_on_submit():
        if current_user.check_password(form.senha_atual.data):
            current_user.set_password(form.nova_senha.data)
            db.session.commit()
            registrar_log(current_user.nome, "Alterou a própria senha", "sucesso")  # ✅ log
            flash("Senha alterada com sucesso!", "success")
            return redirect(url_for("perfil.meu_perfil"))
        else:
            registrar_log(current_user.nome, "Tentativa de alterar senha com senha atual incorreta", "erro")  # ✅ log
            flash("Senha atual incorreta.", "danger")

    return render_template("perfil/meu_perfil.html", usuario=current_user, form=form)

@perfil_bp.route("/editar", methods=["GET", "POST"])
@login_required
def editar_perfil():
    form = EditarPerfilForm(obj=current_user)
    if form.validate_on_submit():
        current_user.nome = form.nome.data
        if "email" in request.form:
            current_user.email = request.form["email"]
        if "ativo" in request.form:
            current_user.ativo = True if request.form["ativo"] == "1" else False
        if "role" in request.form:
            current_user.role = request.form["role"]

        # ❌ Foto removida daqui, será gerenciada apenas em Configurações

        db.session.commit()
        registrar_log(current_user.nome, "Editou o próprio perfil", "sucesso")  # ✅ log
        flash("Perfil atualizado com sucesso!", "success")
        return redirect(url_for("perfil.meu_perfil"))

    return render_template("perfil/editar_perfil.html", form=form, usuario=current_user)

@perfil_bp.route("/senha", methods=["GET", "POST"])
@login_required
def alterar_senha():
    form = AlterarSenhaForm()
    if form.validate_on_submit():
        if current_user.check_password(form.senha_atual.data):
            current_user.set_password(form.nova_senha.data)
            db.session.commit()
            registrar_log(current_user.nome, "Alterou a senha no perfil do usuário", "sucesso")  # ✅ log
            flash("Senha alterada com sucesso!", "success")
            return redirect(url_for("perfil.meu_perfil"))
        else:
            registrar_log(current_user.nome, "Tentativa de alterar senha no perfil do usuário com senha atual incorreta", "erro")  # ✅ log
            flash("Senha atual incorreta.", "danger")
    return render_template("perfil/alterar_senha.html", form=form, usuario=current_user)
