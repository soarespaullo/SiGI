import os
import sys

# Caminho do projeto
sys.path.insert(0, '/var/www/sigi')

# Carregar variáveis de ambiente do .env
from dotenv import load_dotenv
load_dotenv(dotenv_path="/var/www/sigi/.env")

# Importar a aplicação Flask
from app import app as application

