from datetime import datetime
from app.extensions import db   # ✅ importa o db único centralizado em app/extensions.py

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
