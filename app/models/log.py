# app/models/log.py
from app.extensions import db
from datetime import datetime, timezone

class Log(db.Model):
    __tablename__ = "logs"

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100), nullable=False)
    acao = db.Column(db.String(255), nullable=False)
    resultado = db.Column(db.String(50), nullable=False)
    # ✅ Salva sempre em UTC, timezone-aware
    data = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<Log {self.usuario} - {self.acao}>"

# ✅ Função utilitária para registrar logs
def registrar_log(usuario, acao, resultado):
    log = Log(
        usuario=usuario,
        acao=acao,
        resultado=resultado,
        data=datetime.now(timezone.utc)  # sempre UTC
    )
    db.session.add(log)
    db.session.commit()
