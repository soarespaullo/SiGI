import os
from dotenv import load_dotenv
from datetime import timedelta

# Carrega variáveis do .env
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # -----------------------------
    # 🔒 Segurança
    # -----------------------------
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')

    # -----------------------------
    # 🗄️ Banco de Dados
    # -----------------------------
    # Exemplo: export DATABASE_URL="postgresql://user:password@localhost/sigi"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///sigi.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # -----------------------------
    # 📂 Uploads
    # -----------------------------
    UPLOAD_FOLDER = os.path.join(BASE_DIR, os.environ.get('UPLOAD_FOLDER', 'app/static/uploads'))
    TEMPLATES_AUTO_RELOAD = True

    # -----------------------------
    # 📧 Configuração de E-mail
    # -----------------------------
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'mail.riseup.net')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False') == 'True'
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = (
        os.environ.get('MAIL_DEFAULT_NAME', 'SiGI'),
        os.environ.get('MAIL_DEFAULT_EMAIL', 'mail@mail.com')
    )

    # -----------------------------
    # ⏱️ Sessão e Cookies
    # -----------------------------
    # Tempo de vida da sessão (expira automaticamente após X minutos)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=int(os.environ.get('SESSION_TIMEOUT', 30)))

    # Duração do cookie "remember me" do Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(minutes=int(os.environ.get('REMEMBER_TIMEOUT', 30)))

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# -----------------------------
# 🌍 Seleção automática de ambiente
# -----------------------------
def get_config():
    env = os.environ.get("FLASK_ENV", "development")
    if env == "production":
        return ProductionConfig
    return DevelopmentConfig
