from app.extensions import db   # ✅ importa o db único centralizado em app/extensions.py
import secrets
from datetime import datetime

# -----------------------------
# 👥 Membros da Igreja
# -----------------------------
class Member(db.Model):
    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)

    # Dados pessoais
    foto = db.Column(db.String(200))
    nome = db.Column(db.String(120), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=True)
    sexo = db.Column(db.String(20))
    estado_civil = db.Column(db.String(20))
    conjuge = db.Column(db.String(120))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120))

    # Endereço
    endereco = db.Column(db.String(200))
    bairro = db.Column(db.String(100))
    cep = db.Column(db.String(20))

    # Igreja
    batizado = db.Column(db.Boolean, nullable=True)
    dizimista = db.Column(db.Boolean, nullable=True)
    data_batismo = db.Column(db.Date, nullable=True)
    funcao = db.Column(db.String(50))
    status = db.Column(db.String(20))
    data_cadastro = db.Column(db.Date, nullable=True)
    numero_carteira = db.Column(db.String(50))
    igreja_local = db.Column(db.String(120))
    validade = db.Column(db.Date, nullable=True)

    # ➕ Novos campos
    data_conversao = db.Column(db.Date, nullable=True)
    data_saida = db.Column(db.Date, nullable=True)

    # Documentos
    nacionalidade = db.Column(db.String(50))
    naturalidade = db.Column(db.String(50))
    rg = db.Column(db.String(20))
    cpf = db.Column(db.String(20))
    pai = db.Column(db.String(120))
    mae = db.Column(db.String(120))
    filiacao = db.Column(db.String(200))

    # Observações
    observacoes = db.Column(db.Text)

    def __repr__(self):
        return f"<Member {self.nome}>"

# -----------------------------
# 🔗 Links Públicos (ex: cadastro de visitantes)
# -----------------------------
class PublicLink(db.Model):
    __tablename__ = "public_links"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50))  # ex: "visitante"
    hash = db.Column(db.String(64), unique=True, nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def gerar_hash():
        # Gera uma string hex segura de 32 caracteres
        return secrets.token_hex(16)

    def __repr__(self):
        return f"<PublicLink {self.tipo} - {self.hash}>"
