import os
import sys
from dotenv import load_dotenv

# Caminho do projeto
sys.path.insert(0, '/var/www/sigi')

# Carregar variáveis de ambiente
load_dotenv(dotenv_path="/var/www/sigi/.env")

from app import create_app

# Lê FLASK_ENV do .env ou do ambiente
env = os.environ.get("FLASK_ENV", "production")

# Decide qual configuração usar
if env == "production":
    config_class = "config.ProductionConfig"
else:
    config_class = "config.DevelopmentConfig"

application = create_app(config_class)
