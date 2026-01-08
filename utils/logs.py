from app.extensions import db
from app.models.log import Log
from datetime import datetime, timezone
from flask import request

def registrar_log(usuario, tarefa, resultado="sucesso"):
    """
    Registra um log no banco de dados.
    - usuario: e-mail ou identificador do usuário
    - tarefa: ação realizada (ex: login, logout, reset de senha)
    - resultado: 'sucesso', 'erro', 'info', etc.
    """
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
