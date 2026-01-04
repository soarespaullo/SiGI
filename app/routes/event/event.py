from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_mail import Message
from datetime import datetime, timedelta
from app.extensions import db, mail              # ✅ importa db e mail da extensions.py
from app.models import Evento, Member, User      # ✅ importa models do pacote app.models
from app.routes.event.forms import EventoForm    # ✅ ajusta para app.routes
from flask_login import login_required, current_user   # 👈 protege rotas com Flask-Login
from utils.logs import registrar_log             # 👈 importa função de log

event_bp = Blueprint("event", __name__, url_prefix="/eventos")

# -----------------------------
# 📋 Listar eventos com paginação
# -----------------------------
@event_bp.route("/", methods=["GET"])
@login_required   # 👈 protege a rota
def listar_eventos():
    page = request.args.get("page", 1, type=int)

    eventos = Evento.query.order_by(Evento.data_inicio.asc()).paginate(page=page, per_page=10)

    if eventos.total == 0:
        flash("Nenhum evento encontrado", "warning")

    return render_template("eventos/listar_eventos.html", eventos=eventos)

# -----------------------------
# ➕ Criar novo evento
# -----------------------------
@event_bp.route("/novo", methods=["GET", "POST"])
@login_required   # 👈 protege a rota
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
        # 🔐 Define expiração automática pela data de término
        evento.token_expira_em = evento.data_fim

        db.session.add(evento)
        db.session.commit()
        registrar_log(current_user.nome, f"Criou evento: {evento.titulo}", "sucesso")  # 👈 log
        flash("Evento criado com sucesso!", "success")
        return redirect(url_for("event.listar_eventos"))
    return render_template("eventos/novo_evento.html", form=form)

# -----------------------------
# ✏️ Editar evento
# -----------------------------
@event_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required   # 👈 protege a rota
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

        # 🔐 Atualiza expiração do token conforme status
        if evento.status in ["concluido", "cancelado", "concluído"]:
            evento.token_expira_em = datetime.utcnow()
        else:
            evento.token_expira_em = evento.data_fim

        db.session.commit()
        registrar_log(current_user.nome, f"Editou evento: {evento.titulo}", "sucesso")  # 👈 log
        flash("Evento atualizado com sucesso!", "success")
        return redirect(url_for("event.listar_eventos"))
    return render_template("eventos/editar_evento.html", form=form, evento=evento)

# -----------------------------
# ❌ Excluir evento
# -----------------------------
@event_bp.route("/excluir/<int:id>", methods=["POST"])
@login_required   # 👈 protege a rota
def excluir_evento(id):
    evento = Evento.query.get_or_404(id)
    db.session.delete(evento)
    db.session.commit()
    registrar_log(current_user.nome, f"Excluiu evento: {evento.titulo}", "sucesso")  # 👈 log
    flash("Evento excluído com sucesso!", "success")
    return redirect(url_for("event.listar_eventos"))

# -----------------------------
# 🔍 Buscar Eventos com paginação
# -----------------------------
@event_bp.route("/buscar", methods=["GET"])
@login_required   # 👈 protege a rota
def buscar_eventos():
    termo = request.args.get("q", "").strip().lower()
    page = request.args.get("page", 1, type=int)

    query = Evento.query
    if termo:
        query = query.filter(
            (Evento.titulo.ilike(f"%{termo}%")) |
            (Evento.tipo.ilike(f"%{termo}%")) |
            (Evento.organizador.ilike(f"%{termo}%"))
        )

    query = query.order_by(Evento.data_inicio.asc())
    eventos = query.paginate(page=page, per_page=10)

    # 🔹 Só mostra mensagem se realmente houve busca
    if termo:
        if eventos.total == 0:
            flash("Nenhum evento encontrado", "warning")
        elif eventos.total == 1:
            flash("1 evento encontrado", "info")
        else:
            flash(f"{eventos.total} evento(s) encontrado(s)", "info")

    return render_template("eventos/listar_eventos.html", eventos=eventos, termo=termo)

# -----------------------------
# 📧 Enviar lembretes de eventos próximos
# -----------------------------
@event_bp.route("/enviar-lembretes", methods=["GET"])
@login_required   # 👈 protege a rota
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
        registrar_log(current_user.nome, f"Enviou lembrete do evento: {ev.titulo}", "sucesso")  # 👈 log
        print(f"Lembrete enviado para evento: {ev.titulo}")

    flash("Lembretes enviados com sucesso!", "success")
    return redirect(url_for("event.listar_eventos"))
    

# -----------------------------
# 🌐 Página pública por token
# -----------------------------
@event_bp.route("/publico/<string:public_token>", methods=["GET"])
def evento_publico_token(public_token):
    evento = Evento.query.filter_by(public_token=public_token).first_or_404()

    # 🔐 Verifica expiração do token
    if evento.token_expira_em and evento.token_expira_em < datetime.utcnow():
        # Renderiza página amigável de evento expirado
        return render_template("eventos/evento_expirado.html", evento=evento), 410

    return render_template("eventos/evento_publico.html", evento=evento)
