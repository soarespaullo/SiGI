from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.extensions import db                     # ✅ importa db da extensions.py
from app.models import Patrimonio                 # ✅ importa Patrimonio do pacote app.models
from app.routes.patrimonio.forms import PatrimonioForm  # ✅ ajusta para app.routes
from datetime import datetime
from werkzeug.datastructures import MultiDict
from flask_login import login_required, current_user    # 👈 protege rotas com Flask-Login
from utils.logs import registrar_log                     # 👈 importa função de log

patrimonio_bp = Blueprint("patrimonio", __name__, url_prefix="/patrimonios")


def _normalize_date_for_form(formdata: MultiDict, field_name: str = "data_entrada"):
    """Converte yyyy-mm-dd (do input type='date') para dd-mm-aaaa esperado pelo DateField."""
    if field_name in formdata and formdata[field_name]:
        raw = formdata[field_name]
        try:
            iso = datetime.strptime(raw, "%Y-%m-%d").strftime("%d-%m-%Y")
            formdata[field_name] = iso
        except ValueError:
            try:
                datetime.strptime(raw, "%d-%m-%Y")
            except ValueError:
                pass

def _to_float(value):
    """Converte Decimal do WTForms para float do SQLAlchemy (Float)."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

# -----------------------------
# 📋 Listar Patrimônios com paginação
# -----------------------------
@patrimonio_bp.route("/", methods=["GET"])
@login_required   # 👈 protege a rota
def listar_patrimonios():
    page = request.args.get("page", 1, type=int)

    patrimonios = Patrimonio.query.order_by(Patrimonio.nome.asc()).paginate(page=page, per_page=10)

    # 👉 não dispara flash aqui, o template já mostra mensagem quando não há patrimônios
    return render_template("patrimonios/listar_patrimonios.html", patrimonios=patrimonios)


# -----------------------------
# ➕ Criar novo Patrimônio
# -----------------------------
@patrimonio_bp.route("/novo", methods=["GET", "POST"])
@login_required   # 👈 protege a rota
def novo_patrimonio():
    if request.method == "POST":
        formdata = MultiDict(request.form)
        _normalize_date_for_form(formdata)
        form = PatrimonioForm(formdata=formdata)
    else:
        form = PatrimonioForm()

    if form.validate_on_submit():
        item = Patrimonio(
            nome=form.nome.data,
            descricao=form.descricao.data,
            categoria=form.categoria.data,
            numero=form.numero.data,
            valor=_to_float(form.valor.data),
            data_entrada=form.data_entrada.data,
            situacao=form.situacao.data
        )
        db.session.add(item)
        db.session.commit()
        registrar_log(current_user.nome, f"Cadastrou patrimônio: {item.nome}", "sucesso")  # 👈 log
        flash("Patrimônio cadastrado com sucesso!", "success")
        return redirect(url_for("patrimonio.listar_patrimonios"))
    else:
        if request.method == "POST":
            print("Erros de validação:", form.errors)
    return render_template("patrimonios/novo_patrimonio.html", form=form)

# -----------------------------
# ✏️ Editar Patrimônio
# -----------------------------
@patrimonio_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required   # 👈 protege a rota
def editar_patrimonio(id):
    item = Patrimonio.query.get_or_404(id)

    if request.method == "POST":
        formdata = MultiDict(request.form)
        _normalize_date_for_form(formdata)
        form = PatrimonioForm(formdata=formdata, obj=item)
    else:
        form = PatrimonioForm(obj=item)

    if form.validate_on_submit():
        item.nome = form.nome.data
        item.descricao = form.descricao.data
        item.categoria = form.categoria.data
        item.numero = form.numero.data
        item.valor = _to_float(form.valor.data)
        item.data_entrada = form.data_entrada.data
        item.situacao = form.situacao.data

        db.session.commit()
        registrar_log(current_user.nome, f"Editou patrimônio: {item.nome}", "sucesso")  # 👈 log
        flash("Patrimônio atualizado com sucesso!", "success")
        return redirect(url_for("patrimonio.listar_patrimonios"))
    else:
        if request.method == "POST":
            print("Erros de validação:", form.errors)
    return render_template("patrimonios/editar_patrimonio.html", form=form, item=item)


# -----------------------------
# ❌ Excluir Patrimônio
# -----------------------------
@patrimonio_bp.route("/excluir/<int:id>", methods=["POST"])
@login_required   # 👈 protege a rota
def excluir_patrimonio(id):
    item = Patrimonio.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    from utils.logs import registrar_log
    registrar_log(current_user.nome, f"Excluiu patrimônio: {item.nome}", "sucesso")  # 👈 log
    flash("Patrimônio excluído com sucesso!", "info")
    return redirect(url_for("patrimonio.listar_patrimonios"))


# -----------------------------
# 🔍 Buscar Patrimônios com paginação
# -----------------------------
@patrimonio_bp.route("/buscar", methods=["GET"])
@login_required   # 👈 protege a rota
def buscar_patrimonios():
    termo = request.args.get("q", "").strip().lower()
    page = request.args.get("page", 1, type=int)

    query = Patrimonio.query
    if termo:
        query = query.filter(
            (Patrimonio.nome.ilike(f"%{termo}%")) |
            (Patrimonio.categoria.ilike(f"%{termo}%")) |
            (Patrimonio.numero.ilike(f"%{termo}%"))
        )

    query = query.order_by(Patrimonio.nome.asc())
    patrimonios = query.paginate(page=page, per_page=10)

    # 🔹 Só mostra mensagem se realmente houve busca
    if termo:
        if patrimonios.total == 0:
            flash("Nenhum patrimônio corresponde ao termo pesquisado", "warning")
        elif patrimonios.total == 1:
            flash("1 patrimônio encontrado", "info")
        else:
            flash(f"{patrimonios.total} patrimônio(s) encontrados", "info")

        # 👇 log da busca
        from utils.logs import registrar_log
        registrar_log(current_user.nome, f"Buscou patrimônio com termo: {termo}", "sucesso")

    return render_template("patrimonios/listar_patrimonios.html", patrimonios=patrimonios, termo=termo)
    

# -----------------------------
# 📦 Inventário de Patrimônios
# -----------------------------
@patrimonio_bp.route("/inventario", methods=["GET"])
@login_required   # 👈 protege a rota
def inventario():
    categoria = request.args.get("categoria", "").strip()
    situacao = request.args.get("situacao", "").strip()

    query = Patrimonio.query

    if categoria:
        query = query.filter(Patrimonio.categoria.ilike(f"%{categoria}%"))
    if situacao:
        query = query.filter(Patrimonio.situacao == situacao)

    patrimonios = query.order_by(Patrimonio.data_entrada.asc()).all()

    categorias = {}
    total = 0
    for item in patrimonios:
        valor = item.valor or 0
        total += valor
        cat = item.categoria or "Sem categoria"
        if cat in categorias:
            categorias[cat]["qtde"] += 1
            categorias[cat]["valor"] += valor
        else:
            categorias[cat] = {"qtde": 1, "valor": valor}

    if not patrimonios:
        flash("Nenhum patrimônio encontrado para o inventário", "warning")

    from utils.logs import registrar_log
    registrar_log(current_user.nome, "Gerou inventário de patrimônios", "sucesso")  # 👈 log

    return render_template(
        "patrimonios/inventario.html",
        patrimonios=patrimonios,
        categorias=categorias,
        total=total,
        categoria=categoria,
        situacao=situacao
    )
