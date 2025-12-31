import os
import sys
from dotenv import load_dotenv

# Caminho do projeto
sys.path.insert(0, '/var/www/sigi')

# Carregar variáveis de ambiente
load_dotenv(dotenv_path="/var/www/sigi/.env")

from config import get_config
from app import create_app

# Seleciona configuração automaticamente (production ou development)
application = create_app(get_config())
