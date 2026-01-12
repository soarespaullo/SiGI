from app import db
from datetime import datetime

# -----------------------------
# 📋 Modelo para Atas
# -----------------------------
class Ata(db.Model):
    __tablename__ = "atas"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    data_emissao = db.Column(db.Date, nullable=True)

    # ✅ valores padrão ajustados
    tipo = db.Column(db.String(50), nullable=False, server_default="Reunião")
    situacao = db.Column(db.String(20), nullable=False, server_default="Rascunho")

    local = db.Column(db.String(255), nullable=True)
    presidente = db.Column(db.String(255), nullable=True)
    secretario = db.Column(db.String(255), nullable=True)
    participantes = db.Column(db.Text, nullable=True)
    pauta = db.Column(db.Text, nullable=True)
    deliberacoes = db.Column(db.Text, nullable=True)
    observacoes = db.Column(db.Text, nullable=True)

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Ata titulo={self.titulo} tipo={self.tipo} situacao={self.situacao}>"


# -----------------------------
# 📋 Modelo para Certificados
# -----------------------------
class Certificado(db.Model):
    __tablename__ = "certificados"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    data_emissao = db.Column(db.Date, nullable=True)

    criado_por = db.Column(db.String(200), nullable=True)   # Nome do participante
    evento = db.Column(db.String(200), nullable=True)
    corpo = db.Column(db.Text, nullable=True)

    situacao = db.Column(db.String(20), nullable=False, default="enviado")  # enviado, entregue

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Certificado titulo={self.titulo} criado_por={self.criado_por}>"


# -----------------------------
# 📋 Modelo para Cartas
# -----------------------------
class Carta(db.Model):
    __tablename__ = "cartas"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    data_emissao = db.Column(db.Date, nullable=True)

    remetente = db.Column(db.String(200), nullable=True)
    destinatario = db.Column(db.String(200), nullable=True)
    cidade = db.Column(db.String(100), nullable=True)
    corpo = db.Column(db.Text, nullable=True)

    situacao = db.Column(db.String(20), nullable=False, default="enviado")

    # vínculo com membro (se quiser manter)
    membro_id = db.Column(
        db.Integer,
        db.ForeignKey("members.id", ondelete="SET NULL"),
        nullable=True
    )
    membro = db.relationship("Member", backref="cartas")

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Carta titulo={self.titulo} remetente={self.remetente}>"
