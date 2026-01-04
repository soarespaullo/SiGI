from flask import Blueprint, render_template, abort, request
from flask_login import login_required, current_user
from functools import wraps
from app.models.log import Log

logs_bp = Blueprint("logs", __name__, url_prefix="/logs")

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@logs_bp.route("/", methods=["GET"])
@admin_required
def visualizar_logs():
    # 🔹 Captura parâmetros da query string
    page = request.args.get("page", 1, type=int)
    usuario = request.args.get("usuario", "").strip()

    query = Log.query
    if usuario:
        query = query.filter(Log.usuario.ilike(f"%{usuario}%"))

    registros = query.order_by(Log.data.desc()).paginate(page=page, per_page=20)

    return render_template("admin/logs.html", registros=registros, usuario=usuario)
