from datetime import datetime
from app.extensions import db	# ✅ importa o db único centralizado em app/extensions.py

# -----------------------------
# 💰 Financeiro
# -----------------------------
TIPOS_FINANCEIRO = ("Entrada", "Saída")

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

    def __init__(self, **kwargs):
        tipo = kwargs.get("tipo")
        if tipo not in TIPOS_FINANCEIRO:
            raise ValueError("Tipo deve ser 'Entrada' ou 'Saída'")
        super().__init__(**kwargs)

    def __repr__(self):
        data_str = self.data.strftime('%d-%m-%Y') if self.data else "sem data"
        return f"<Financeiro {self.tipo} {self.categoria} R${self.valor:.2f} em {data_str}>"
