from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from app.extensions import db, mail
from app.models import User
from .forms import SetupForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from datetime import datetime
from flask_login import login_user, logout_user   # 👈 importa funções do Flask-Login

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
        admin = User(email=form.email.data.lower())
        admin.set_password(form.senha.data)
        db.session.add(admin)
        db.session.commit()
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
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.senha.data):
            # 🔑 Usa Flask-Login para autenticar
            login_user(user, remember=True)
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash("E-mail ou senha inválidos.", "danger")
    return render_template('auth/login.html', form=form, hide_navbar=True, hide_footer=True)

# ===========================
# Rota: /auth/logout
# ===========================
@auth_bp.route('/logout')
def logout():
    logout_user()   # 👈 usa Flask-Login para encerrar sessão
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

            # ✅ Tratamento de erro no envio
            try:
                mail.send(msg)
            except Exception as e:
                current_app.logger.error(f"Erro ao enviar e-mail: {e}")
                flash("Não foi possível enviar o e-mail agora. Tente novamente mais tarde.", "danger")

        # Mensagem genérica para não revelar se o e-mail existe ou não
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
        flash("Senha redefinida com sucesso!", "success")
        return redirect(url_for('auth.login'))
    elif form.is_submitted() and not form.validate_on_submit():
        flash("As senhas devem coincidir.", "danger")

    return render_template('auth/reset_password.html', form=form, hide_navbar=True, hide_footer=True)
