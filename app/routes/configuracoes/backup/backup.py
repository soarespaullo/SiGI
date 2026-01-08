from flask import Blueprint, render_template, flash, redirect, url_for, abort, send_file
from flask_login import login_required, current_user
from functools import wraps
from dotenv import load_dotenv
import os, subprocess, re, tempfile, zipfile, urllib.parse
from datetime import datetime

from utils.logs import registrar_log

backup_bp = Blueprint("backup", __name__, url_prefix="/backup")

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@backup_bp.route("/", methods=["GET"])
@admin_required
def backup_page():
    return render_template("configuracoes/backup.html")

@backup_bp.route("/gerar", methods=["POST"])
@admin_required
def gerar_backup():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")

    match = re.match(r"mysql\+pymysql://(.+):(.+)@(.+):(\d+)/(.+)", db_url or "")
    if not match:
        flash("DATABASE_URL inválido ou não configurado.", "danger")
        return redirect(url_for("configuracoes.backup.backup_page"))

    user, password, host, port, dbname = match.groups()
    password = urllib.parse.unquote(password)  # decodifica %40 → @

    data_str = datetime.now().strftime("%d-%m-%Y")

    tmp_sql = tempfile.NamedTemporaryFile(delete=False, suffix=".sql")
    tmp_sql.close()

    try:
        subprocess.run(
            ["mysqldump", "-h", host, "-P", port, "-u", user, f"-p{password}", dbname],
            stdout=open(tmp_sql.name, "w"),
            check=True
        )

        zip_filename = f"{dbname}_backup_{data_str}.zip"
        tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        tmp_zip.close()

        with zipfile.ZipFile(tmp_zip.name, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(tmp_sql.name, arcname=f"{dbname}_backup_{data_str}.sql")

        registrar_log(current_user.nome or "desconhecido",
                      f"Gerou backup do banco {dbname}", "sucesso")
        return send_file(tmp_zip.name, as_attachment=True, download_name=zip_filename)

    except Exception as e:
        registrar_log(current_user.nome or "desconhecido",
                      f"Erro ao gerar backup do banco {dbname}", "erro")
        flash(f"Erro ao gerar backup: {e}", "danger")
        return redirect(url_for("configuracoes.backup.backup_page"))
    finally:
        if os.path.exists(tmp_sql.name):
            os.remove(tmp_sql.name)
