from app import db
from datetime import datetime

class Documento(db.Model):
    __tablename__ = "documentos"

    id = db.Column(db.Integer, primary_key=True)

    # Campos básicos
    titulo = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)   # Ex.: 'Reunião', 'Fundação', etc.
    situacao = db.Column(db.String(20), nullable=False, default="Rascunho")  # <-- novo campo
    data = db.Column(db.Date, nullable=True)
    descricao = db.Column(db.Text, nullable=True)
    arquivo = db.Column(db.String(255), nullable=True)
    criado_por = db.Column(db.String(100), nullable=True)

    # Campos adicionais para atas
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
        return f"<Documento tipo={self.tipo} situacao={self.situacao} titulo={self.titulo}>"
