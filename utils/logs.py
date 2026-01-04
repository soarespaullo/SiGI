from app import db
from app.models import Log

def registrar_log(usuario, acao, resultado="sucesso"):
    novo_log = Log(usuario=usuario, acao=acao, resultado=resultado)
    db.session.add(novo_log)
    db.session.commit()
