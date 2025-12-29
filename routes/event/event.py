from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_mail import Message
from datetime import datetime, timedelta
from extensions import db, mail   # ✅ db e mail vêm daqui
from models import Evento, Member, User  # ✅ apenas os models
from routes.event.forms import EventoForm


event_bp = Blueprint("event", __name__, url_prefix="/eventos")

# -----------------------------
# 📋 Listar eventos
# -----------------------------
@event_bp.route("/", methods=["GET"])
def listar_eventos():
    eventos = Evento.query.order_by(Evento.data_inicio.asc()).all()
    if not eventos:
        flash("Nenhum evento encontrado", "warning")
    return render_template("eventos/listar_eventos.html", eventos=eventos)

# -----------------------------
# ➕ Criar novo evento
# -----------------------------
@event_bp.route("/novo", methods=["GET", "POST"])
def novo_evento():
    form = EventoForm()
    if form.validate_on_submit():
        evento = Evento(
            titulo=form.titulo.data,
            descricao=form.descricao.data,
            tipo=form.tipo.data,
            data_inicio=form.data_inicio.data,
            data_fim=form.data_fim.data,
            local=form.local.data,
            organizador=form.organizador.data,
            status=form.status.data
        )
        db.session.add(evento)
        db.session.commit()
        flash("Evento criado com sucesso!", "success")
        return redirect(url_for("event.listar_eventos"))
    return render_template("eventos/novo_evento.html", form=form)

# -----------------------------
# ✏️ Editar evento
# -----------------------------
@event_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_evento(id):
    evento = Evento.query.get_or_404(id)
    form = EventoForm(obj=evento)
    if form.validate_on_submit():
        evento.titulo = form.titulo.data
        evento.descricao = form.descricao.data
        evento.tipo = form.tipo.data
        evento.data_inicio = form.data_inicio.data
        evento.data_fim = form.data_fim.data
        evento.local = form.local.data
        evento.organizador = form.organizador.data
        evento.status = form.status.data

        db.session.commit()
        flash("Evento atualizado com sucesso!", "success")
        return redirect(url_for("event.listar_eventos"))
    return render_template("eventos/editar_evento.html", form=form, evento=evento)

# -----------------------------
# ❌ Excluir evento
# -----------------------------
@event_bp.route("/excluir/<int:id>", methods=["POST"])
def excluir_evento(id):
    evento = Evento.query.get_or_404(id)
    db.session.delete(evento)
    db.session.commit()
    flash("Evento excluído com sucesso!", "success")
    return redirect(url_for("event.listar_eventos"))

# -----------------------------
# 🔍 Buscar eventos
# -----------------------------
@event_bp.route("/buscar", methods=["GET"])
def buscar_eventos():
    termo = request.args.get("q", "").strip().lower()

    if termo:
        eventos = Evento.query.filter(
            (Evento.titulo.ilike(f"%{termo}%")) |
            (Evento.tipo.ilike(f"%{termo}%")) |
            (Evento.organizador.ilike(f"%{termo}%"))
        ).order_by(Evento.data_inicio.asc()).all()
    else:
        eventos = Evento.query.order_by(Evento.data_inicio.asc()).all()

    if not eventos:
        flash("Nenhum evento encontrado", "warning")
    elif len(eventos) == 1:
        flash("1 evento encontrado", "info")
    else:
        flash(f"{len(eventos)} evento(s) encontrado(s)", "info")

    return render_template("eventos/listar_eventos.html", eventos=eventos)


# -----------------------------
# 📧 Enviar lembretes de eventos próximos
# -----------------------------
@event_bp.route("/enviar-lembretes", methods=["GET"])
def enviar_lembretes_eventos():
    hoje = datetime.now()
    limite = hoje + timedelta(days=3)  # próximos 3 dias

    # Busca eventos que começam nos próximos 3 dias
    eventos = Evento.query.filter(
        Evento.data_inicio >= hoje,
        Evento.data_inicio <= limite
    ).all()

    if not eventos:
        flash("Nenhum evento próximo para enviar lembrete.", "info")
        return redirect(url_for("event.listar_eventos"))

    # ✅ pega todos os e-mails dos membros
    member_emails = [m.email.strip() for m in Member.query.filter(Member.email != None).all() if m.email.strip()]

    # ✅ pega o e-mail do administrador
    admin = User.query.filter_by(role="admin").first()
    admin_email = admin.email if admin else None

    # ✅ junta tudo em uma lista de destinatários
    recipients = member_emails
    if admin_email:
        recipients.append(admin_email)

    for ev in eventos:
        html_body = render_template("email/lembrete_evento.html", evento=ev)

        msg = Message(
            subject=f"Lembrete: {ev.titulo} está chegando!",
            recipients=recipients,   # envia para membros + admin
            html=html_body
        )
        mail.send(msg)
        print(f"Lembrete enviado para evento: {ev.titulo}")

    flash("Lembretes enviados com sucesso!", "success")
    return redirect(url_for("event.listar_eventos"))

