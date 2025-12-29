from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from extensions import db   # ✅ importa o db único daqui

# -----------------------------
# 👤 Usuário (Admin / Login)
# -----------------------------
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="admin")
    nome = db.Column(db.String(100), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"

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
# 📅 Eventos
# -----------------------------
class Evento(db.Model):
    __tablename__ = "eventos"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=True)

    tipo = db.Column(db.String(50), nullable=False)
    data_inicio = db.Column(db.DateTime, nullable=False)
    data_fim = db.Column(db.DateTime, nullable=False)

    local = db.Column(db.String(150), nullable=True)
    organizador = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="ativo")

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        data_str = self.data_inicio.strftime('%d/%m/%Y %H:%M') if self.data_inicio else "sem data"
        return f"<Evento {self.titulo} - {data_str}>"

# -----------------------------
# 💰 Financeiro
# -----------------------------
class Financeiro(db.Model):
    __tablename__ = "financeiro"

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    valor = db.Column(db.Float, nullable=False, default=0.0)

    tipo = db.Column(db.String(20), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    conta = db.Column(db.String(100), nullable=False, default="Caixa")
    descricao = db.Column(db.String(200))

    cpf_membro = db.Column(db.String(14))
    cnpj_fornecedor = db.Column(db.String(18))

    conciliado = db.Column(db.Boolean, default=False)
    comprovante = db.Column(db.String(200))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        data_str = self.data.strftime('%d-%m-%Y') if self.data else "sem data"
        return f"<Financeiro {self.tipo} {self.categoria} R${self.valor:.2f} em {data_str}>"

# -----------------------------
# 📦 Patrimônio
# -----------------------------
class Patrimonio(db.Model):
    __tablename__ = "patrimonios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    categoria = db.Column(db.String(100), default="Não categorizado")
    numero = db.Column(db.String(50), nullable=True)
    valor = db.Column(db.Float, nullable=True, default=0.0)
    data_entrada = db.Column(db.Date, nullable=True)
    situacao = db.Column(db.String(50), default="Ativo")

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        data_str = self.data_entrada.strftime('%d-%m-%Y') if self.data_entrada else "sem data"
        return f"<Patrimonio {self.nome} ({self.categoria}) - {data_str}>"
