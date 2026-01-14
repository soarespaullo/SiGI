from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models.log import Log
from app.extensions import db
from datetime import datetime, timedelta

# ✅ Blueprint precisa se chamar logs_bp
logs_bp = Blueprint("logs", __name__, url_prefix="/logs")

@logs_bp.route("/", methods=["GET"])
@login_required
def visualizar_logs():
    page = request.args.get("page", 1, type=int)
    usuario = request.args.get("usuario", "", type=str)

    query = Log.query
    if usuario:
        query = query.filter(Log.usuario.ilike(f"%{usuario}%"))

    # ✅ Ordena por datahora e pagina com 20 registros
    registros = query.order_by(Log.datahora.desc()).paginate(page=page, per_page=20)

    return render_template("configuracoes/logs.html", registros=registros, usuario=usuario)


# ✅ Remove apenas os registros mais antigos que 30 dias e confirma a exclusão no banco
@logs_bp.route("/remover_logs", methods=["GET"])
@login_required
def remover_logs():
    limite = datetime.now() - timedelta(days=30)
    qtd = Log.query.filter(Log.datahora < limite).delete(synchronize_session=False)
    db.session.commit()

    if qtd > 0:
        flash(f"{qtd} logs antigos foram removidos (30 dias ou mais).", "info")
    else:
        flash("Nenhum log com mais de 30 dias encontrado para remoção.", "warning")

    return redirect(url_for("configuracoes.logs.visualizar_logs"))



