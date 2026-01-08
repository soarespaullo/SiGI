from app.extensions import db
from datetime import datetime, timezone
from flask import request

class Log(db.Model):
    __tablename__ = "logs"

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100), nullable=False)
    tarefa = db.Column(db.String(255), nullable=False)
    resultado = db.Column(db.String(50), nullable=False)

    # ✅ Campo único DateTime com timezone (UTC)
    datahora = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    ip = db.Column(db.String(45), nullable=False)

    def __repr__(self):
        return f"<Log {self.usuario} - {self.tarefa}>"

# ✅ Função utilitária para registrar logs
def registrar_log(usuario, tarefa, resultado="sucesso"):
    try:
        log = Log(
            usuario=usuario,
            tarefa=tarefa,
            resultado=resultado,
            datahora=datetime.now(timezone.utc),
            ip=request.remote_addr or "desconhecido"
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao registrar log: {e}")
