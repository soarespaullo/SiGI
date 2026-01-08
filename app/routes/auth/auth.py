from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from app.extensions import db, mail
from app.models import User
from .forms import SetupForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from datetime import datetime
from flask_login import login_user, logout_user, current_user   # 👈 importa também current_user
from utils.logs import registrar_log              # 👈 importa função de log

auth_bp = Blueprint('auth', __name__)

def get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

# ===========================
# Rota: /auth/
# ===========================
@auth_bp.route('/')
def index():
    if User.query.first() is None:
        return redirect(url_for('auth.setup'))
    else:
        return redirect(url_for('auth.login'))

# ===========================
# Rota: /auth/setup
# ===========================
@auth_bp.route('/setup', methods=['GET', 'POST'])
def setup():
    if User.query.first() is not None:
        flash("Já existe um administrador configurado.", "warning")
        return redirect(url_for('auth.login'))

    form = SetupForm()
    if form.validate_on_submit():
        admin = User(
            nome=form.nome.data,                     # ✅ agora salva o nome
            email=form.email.data.lower(),
            ativo=True,
            role="admin"                             # opcional: já define como admin
        )
        admin.set_password(form.senha.data)
        db.session.add(admin)
        db.session.commit()
        registrar_log(admin.nome or "desconhecido", "Configuração inicial concluída", "sucesso")
        flash("Configuração concluída! Faça login.", "success")
        return redirect(url_for('auth.login'))
    elif form.is_submitted() and not form.validate_on_submit():
        flash("As senhas devem coincidir.", "danger")

    return render_template('auth/setup.html', form=form, hide_navbar=True, hide_footer=True)


# ===========================
# Rota: /auth/login
# ===========================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # 🔹 Se não existe nenhum usuário configurado, força ir para setup
    if User.query.first() is None:
        flash("Nenhum usuário configurado. Faça a configuração inicial primeiro.", "warning")
        return redirect(url_for('auth.setup'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if user and user.check_password(form.senha.data):
            # Usuário existe e senha correta
            if not getattr(user, "ativo", True):
                flash("Usuário desativado. Entre em contato com o administrador.", "danger")
                registrar_log(user.nome or "desconhecido",
                              "Tentativa de login com usuário desativado",
                              "erro")
                return redirect(url_for('auth.login'))

            login_user(user, remember=True)
            registrar_log(user.nome or "desconhecido",
                          "Login realizado",
                          "sucesso")
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for('dashboard.dashboard'))

        else:
            # Login inválido
            flash("E-mail ou senha inválidos.", "danger")
            if user:
                # 🔹 E-mail existe, mas senha incorreta → loga pelo nome
                registrar_log(user.nome or "desconhecido",
                              "Tentativa de login inválida (senha incorreta)",
                              "erro")
            else:
                # 🔹 E-mail não existe → loga o e-mail informado
                registrar_log(form.email.data.lower() or "não informado",
                              "Tentativa de login inválida (usuário inexistente)",
                              "erro")

    return render_template('auth/login.html',
                           form=form,
                           hide_navbar=True,
                           hide_footer=True)


# ===========================
# Rota: /auth/logout
# ===========================
@auth_bp.route('/logout')
def logout():
    if hasattr(current_app, "login_manager") and current_app.login_manager._login_disabled is False:
        if current_user.is_authenticated:
            registrar_log(current_user.nome or "desconhecido", "Logout realizado", "sucesso")  # 👈 log seguro
    logout_user()
    flash("Logout realizado com sucesso!", "info")
    return redirect(url_for('auth.login'))

# ===========================
# Rota: /auth/forgot_password
# ===========================
@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            serializer = get_serializer()
            token = serializer.dumps(user.email, salt="reset-password")
            reset_url = url_for('auth.reset_password', token=token, _external=True)

            msg = Message(
                subject="🔒 Redefinição de senha - SiGI",
                recipients=[user.email]
            )
            msg.html = render_template(
                "email/reset_password.html",
                user_email=user.email,
                reset_url=reset_url,
                current_year=datetime.now().year
            )

            try:
                mail.send(msg)
                registrar_log(user.nome or "desconhecido", "Solicitou redefinição de senha", "sucesso")  # 👈 log seguro
            except Exception as e:
                current_app.logger.error(f"Erro ao enviar e-mail: {e}")
                registrar_log(user.nome or "desconhecido", "Erro ao enviar e-mail de redefinição", "erro")  # 👈 log seguro
                flash("Não foi possível enviar o e-mail agora. Tente novamente mais tarde.", "danger")

        flash("Se o e-mail existir, enviaremos instruções de redefinição.", "info")
        return redirect(url_for('auth.login'))

    return render_template(
        'auth/forgot_password.html',
        form=form,
        hide_navbar=True,
        hide_footer=True
    )

# ===========================
# Rota: /auth/reset_password/<token>
# ===========================
@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    serializer = get_serializer()
    try:
        email = serializer.loads(token, salt="reset-password", max_age=3600)
    except (SignatureExpired, BadSignature):
        flash("Link inválido ou expirado.", "danger")
        return redirect(url_for('auth.forgot_password'))

    user = User.query.filter_by(email=email).first_or_404()
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.senha.data)
        db.session.commit()
        registrar_log(user.nome or "desconhecido", "Senha redefinida", "sucesso")  # 👈 log seguro
        flash("Senha redefinida com sucesso!", "success")
        return redirect(url_for('auth.login'))
    elif form.is_submitted() and not form.validate_on_submit():
        flash("As senhas devem coincidir.", "danger")

    return render_template('auth/reset_password.html', form=form, hide_navbar=True, hide_footer=True)
