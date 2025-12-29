from flask import Blueprint, render_template, redirect, url_for, flash, request
from models import db, Patrimonio
from .forms import PatrimonioForm
from datetime import datetime
from werkzeug.datastructures import MultiDict

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
# 📋 Listar Patrimônios
# -----------------------------
@patrimonio_bp.route("/", methods=["GET"])
def listar_patrimonios():
    patrimonios = Patrimonio.query.order_by(Patrimonio.nome.asc()).all()
    if not patrimonios:
        flash("Nenhum patrimônio encontrado", "warning")
    return render_template("patrimonios/listar_patrimonios.html", patrimonios=patrimonios)

# -----------------------------
# ➕ Criar novo Patrimônio
# -----------------------------
@patrimonio_bp.route("/novo", methods=["GET", "POST"])
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
def excluir_patrimonio(id):
    item = Patrimonio.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash("Patrimônio excluído com sucesso!", "info")
    return redirect(url_for("patrimonio.listar_patrimonios"))

# -----------------------------
# 🔍 Buscar Patrimônios
# -----------------------------
@patrimonio_bp.route("/buscar", methods=["GET"])
def buscar_patrimonios():
    termo = request.args.get("q", "").strip().lower()

    if termo:
        patrimonios = Patrimonio.query.filter(
            (Patrimonio.nome.ilike(f"%{termo}%")) |
            (Patrimonio.categoria.ilike(f"%{termo}%")) |
            (Patrimonio.numero.ilike(f"%{termo}%"))
        ).order_by(Patrimonio.nome.asc()).all()
    else:
        patrimonios = Patrimonio.query.order_by(Patrimonio.nome.asc()).all()

    if not patrimonios:
        flash("Nenhum patrimônio encontrado", "warning")
    elif len(patrimonios) == 1:
        flash("1 patrimônio encontrado", "info")
    else:
        flash(f"{len(patrimonios)} patrimônio(s) encontrado(s)", "info")

    return render_template("patrimonios/listar_patrimonios.html", patrimonios=patrimonios)

# -----------------------------
# 📦 Inventário de Patrimônios
# -----------------------------
@patrimonio_bp.route("/inventario", methods=["GET"])
def inventario():
    patrimonios = Patrimonio.query.order_by(Patrimonio.data_entrada.asc()).all()

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

    return render_template(
        "patrimonios/inventario.html",
        patrimonios=patrimonios,
        categorias=categorias,
        total=total
    )
