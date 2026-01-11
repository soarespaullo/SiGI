from flask import Blueprint, render_template, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from functools import wraps
from dotenv import set_key
import os
from .forms import MailConfigForm
from utils.logs import registrar_log

# Lê o caminho do .env a partir da variável DOTENV_PATH
dotenv_path = os.environ.get("DOTENV_PATH", os.path.join(os.path.dirname(__file__), "..", ".env"))

mail_bp = Blueprint("mail", __name__, url_prefix="/mail")

# Decorator para garantir acesso apenas a administradores
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@mail_bp.route("/", methods=["GET", "POST"])
@admin_required
def configurar_mail():
    form = MailConfigForm()

    if form.validate_on_submit():
        set_key(dotenv_path, "MAIL_SERVER", form.mail_server.data)
        set_key(dotenv_path, "MAIL_PORT", str(form.mail_port.data))
        set_key(dotenv_path, "MAIL_USE_TLS", str(form.mail_use_tls.data))
        set_key(dotenv_path, "MAIL_USE_SSL", str(form.mail_use_ssl.data))
        set_key(dotenv_path, "MAIL_USERNAME", form.mail_username.data)
        set_key(dotenv_path, "MAIL_PASSWORD", form.mail_password.data)
        set_key(dotenv_path, "MAIL_DEFAULT_NAME", form.mail_default_name.data)
        set_key(dotenv_path, "MAIL_DEFAULT_EMAIL", form.mail_default_email.data)

        registrar_log(current_user.nome, "Atualizou configurações de e-mail", "sucesso")
        flash("Configurações de e-mail salvas com sucesso!", "success")
        return redirect(url_for("configuracoes.mail.configurar_mail"))

    return render_template("configuracoes/config_mail.html", form=form)
