from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from functools import wraps

# Blueprint principal de Configurações
config_bp = Blueprint("configuracoes", __name__, url_prefix="/configuracoes")

# Decorator para garantir acesso apenas a administradores
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)  # bloqueia se não for admin
        return f(*args, **kwargs)
    return decorated_function

# importa os submódulos
from .usuarios.usuarios import usuarios_bp
from .backup.backup import backup_bp
from .mail.mail import mail_bp  
from .logs.logs import logs_bp

# registra os sub-blueprints dentro do config_bp
config_bp.register_blueprint(usuarios_bp)
config_bp.register_blueprint(backup_bp)
config_bp.register_blueprint(mail_bp)  
config_bp.register_blueprint(logs_bp)

# rota de configurações para compatibilidade
@config_bp.route("/")
@admin_required   # 🔹 agora só acessa se estiver logado e for admin
def configuracoes():
    return render_template("configuracoes/configuracoes.html")

