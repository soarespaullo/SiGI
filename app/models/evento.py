from datetime import datetime
import uuid
from app.extensions import db   # ✅ importa o db único centralizado em app/extensions.py

# -----------------------------
# 📅 Eventos
# -----------------------------
class Evento(db.Model):
    __tablename__ = "eventos"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=True)

    # 🔹 Tipos de evento permitidos
    TIPOS_EVENTO = [
        "culto especial",
        "retiro",
        "batismo",
        "reunião",
        "evangelismo",
        "conferência",
        "outros"
    ]

    tipo = db.Column(db.String(50), nullable=False)

    data_inicio = db.Column(db.DateTime, nullable=False)
    data_fim = db.Column(db.DateTime, nullable=False)

    local = db.Column(db.String(150), nullable=True)
    organizador = db.Column(db.String(100), nullable=True)

    # 🔹 Status permitidos
    STATUS_EVENTO = [
        "confirmado",
        "planejado",
        "em andamento",
        "concluído",
        "cancelado"
    ]

    status = db.Column(db.String(20), nullable=False, default="confirmado")

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔗 Token público único para compartilhamento
    public_token = db.Column(
        db.String(16),
        unique=True,
        nullable=False,
        default=lambda: uuid.uuid4().hex[:12]
    )

    # 🔐 Data de expiração do token público
    token_expira_em = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        data_str = self.data_inicio.strftime('%d/%m/%Y %H:%M') if self.data_inicio else "sem data"
        return f"<Evento {self.titulo} - {data_str}>"
