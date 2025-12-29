from dotenv import load_dotenv
load_dotenv()  # 🔄 Carrega variáveis do arquivo .env

import os
from flask import Flask
from extensions import db, mail, migrate
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

# -----------------------------
# 🔒 Segurança e Configurações básicas
# -----------------------------
# Usa variáveis de ambiente para não expor credenciais no código
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')

# -----------------------------
# 🗄️ Banco de Dados
# -----------------------------
# Exemplo: export DATABASE_URL="postgresql://user:password@localhost/sigi"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///sigi.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# -----------------------------
# 📂 Uploads
# -----------------------------
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'static/uploads')
app.config['TEMPLATES_AUTO_RELOAD'] = True

# -----------------------------
# 📧 Configuração de E-mail
# -----------------------------
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'mail.riseup.net')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'False') == 'True'
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = (
    os.environ.get('MAIL_DEFAULT_NAME', 'SiGI'),
    os.environ.get('MAIL_DEFAULT_EMAIL', 'psinformatica@riseup.net')
)

# -----------------------------
# 🔗 Inicializa extensões
# -----------------------------
db.init_app(app)
mail.init_app(app)
migrate.init_app(app, db)

# Proteção contra CSRF em formulários
csrf = CSRFProtect(app)

# -----------------------------
# 📌 Importa e registra os Blueprints
# -----------------------------
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.event import event_bp
from routes.financeiro import financeiro_bp
from routes.member import member_bp
from routes.patrimonio import patrimonio_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(event_bp)
app.register_blueprint(financeiro_bp)
app.register_blueprint(member_bp)
app.register_blueprint(patrimonio_bp)

# -----------------------------
# 🗄️ Cria o banco de dados e tabelas
# -----------------------------
#with app.app_context():
#    db.create_all()

# -----------------------------
# 📅 Context processor para ano atual
# -----------------------------
@app.context_processor
def inject_globals():
    from datetime import datetime
    return {'current_year': datetime.now().year}

# -----------------------------
# 🚀 Inicialização da aplicação
# -----------------------------
if __name__ == "__main__":
    # Em produção, debug deve ser False
    debug = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    app.run(debug=debug)
