from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, send_file
from flask_login import login_required, current_user
from functools import wraps
from dotenv import load_dotenv
import os, subprocess, re, tempfile, zipfile
from datetime import datetime

from utils.logs import registrar_log   # 👈 importa função de log

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
    return render_template("admin/backup.html")

@backup_bp.route("/gerar", methods=["POST"])
@admin_required
def gerar_backup():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")

    match = re.match(r"mysql\+pymysql://(.+):(.+)@(.+):(\d+)/(.+)", db_url or "")
    if not match:
        flash("DATABASE_URL inválido ou não configurado.", "danger")
        return redirect(url_for("admin.backup.backup_page"))

    user, password, host, port, dbname = match.groups()

    # 🔹 Data no formato DD-MM-YYYY
    data_str = datetime.now().strftime("%d-%m-%Y")

    # 🔹 Arquivo temporário para o .sql
    tmp_sql = tempfile.NamedTemporaryFile(delete=False, suffix=".sql")
    tmp_sql.close()

    try:
        subprocess.run(
            ["mysqldump", "-h", host, "-P", port, "-u", user, f"-p{password}", dbname],
            stdout=open(tmp_sql.name, "w"),
            check=True
        )

        # 🔹 Criar o .zip temporário
        zip_filename = f"{dbname}_backup_{data_str}.zip"
        tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        tmp_zip.close()

        with zipfile.ZipFile(tmp_zip.name, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(tmp_sql.name, arcname=f"{dbname}_backup_{data_str}.sql")

        registrar_log(current_user.nome, f"Gerou backup do banco {dbname}", "sucesso")  # 👈 log
        return send_file(tmp_zip.name, as_attachment=True, download_name=zip_filename)

    except Exception as e:
        registrar_log(current_user.nome, f"Erro ao gerar backup do banco {dbname}", "erro")  # 👈 log
        flash(f"Erro ao gerar backup: {e}", "danger")
        return redirect(url_for("admin.backup.backup_page"))
    finally:
        # remove o .sql temporário
        if os.path.exists(tmp_sql.name):
            os.remove(tmp_sql.name)


@backup_bp.route("/restaurar", methods=["POST"])
@admin_required
def restaurar_backup():
    file = request.files.get("backup_file")
    if file:
        filename = secure_filename(file.filename)

        # 🔹 Salva o .zip temporário
        import tempfile, zipfile
        tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        file.save(tmp_zip.name)

        # 🔹 Extrai o .sql de dentro do .zip
        sql_path = None
        with zipfile.ZipFile(tmp_zip.name, "r") as zipf:
            for member in zipf.namelist():
                if member.endswith(".sql"):
                    sql_path = tempfile.NamedTemporaryFile(delete=False, suffix=".sql").name
                    zipf.extract(member, os.path.dirname(sql_path))
                    # move para o caminho temporário
                    os.rename(os.path.join(os.path.dirname(sql_path), member), sql_path)
                    break

        if not sql_path:
            flash("Nenhum arquivo .sql encontrado dentro do .zip.", "danger")
            return redirect(url_for("admin.backup.backup_page"))

        # 🔹 Carrega dados do banco do .env
        from dotenv import load_dotenv
        load_dotenv()
        db_url = os.getenv("DATABASE_URL")
        import re
        match = re.match(r"mysql\+pymysql://(.+):(.+)@(.+):(\d+)/(.+)", db_url or "")
        if not match:
            flash("DATABASE_URL inválido ou não configurado.", "danger")
            return redirect(url_for("admin.backup.backup_page"))

        user, password, host, port, dbname = match.groups()

        try:
            subprocess.run(
                ["mysql", "-h", host, "-P", port, "-u", user, f"-p{password}", dbname],
                stdin=open(sql_path, "r"),
                check=True
            )
            registrar_log(current_user.nome, f"Restaurou backup do banco {dbname}", "sucesso")  # 👈 log
            flash("Backup restaurado com sucesso!", "success")
        except Exception as e:
            registrar_log(current_user.nome, f"Erro ao restaurar backup do banco {dbname}", "erro")  # 👈 log
            flash(f"Erro ao restaurar backup: {e}", "danger")
        finally:
            # remove temporários
            if os.path.exists(tmp_zip.name):
                os.remove(tmp_zip.name)
            if sql_path and os.path.exists(sql_path):
                os.remove(sql_path)
    else:
        flash("Nenhum arquivo enviado.", "danger")

    return redirect(url_for("admin.backup.backup_page"))
