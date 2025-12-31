import os
from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from app.extensions import db, mail, migrate
from config import get_config   # ✅ importa a função que decide o ambiente

csrf = CSRFProtect()

def create_app(config_class=None):
    # Cria a instância do Flask
    app = Flask(__name__)
    # Usa configuração automática (production ou development conforme FLASK_ENV)
    app.config.from_object(config_class or get_config())

    # -----------------------------
    # 🔗 Inicializa extensões
    # -----------------------------
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # -----------------------------
    # 👤 Configuração do LoginManager
    # -----------------------------
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"   # rota para redirecionar
    login_manager.login_message = "Sua sessão expirou. Faça login novamente."
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    # 🔹 Função para carregar usuário pelo ID (necessário para Flask-Login)
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # -----------------------------
    # 📌 Importa e registra os Blueprints
    # -----------------------------
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.event import event_bp
    from app.routes.financeiro import financeiro_bp
    from app.routes.member import member_bp
    from app.routes.patrimonio import patrimonio_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(financeiro_bp)
    app.register_blueprint(member_bp)
    app.register_blueprint(patrimonio_bp)

    # -----------------------------
    # 📅 Context processor para ano atual
    # -----------------------------
    @app.context_processor
    def inject_globals():
        from datetime import datetime
        return {'current_year': datetime.now().year}

    # -----------------------------
    # ⚠️ Handlers globais de erro
    # -----------------------------
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("errors/500.html"), 500

    return app
