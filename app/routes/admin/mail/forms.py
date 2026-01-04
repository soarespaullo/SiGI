from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, NumberRange

class MailConfigForm(FlaskForm):
    mail_server = StringField("Servidor SMTP", validators=[DataRequired()])
    mail_port = IntegerField("Porta", validators=[DataRequired(), NumberRange(min=1, max=65535)])
    mail_use_tls = BooleanField("Usar TLS")
    mail_use_ssl = BooleanField("Usar SSL")
    mail_username = StringField("Usuário", validators=[DataRequired()])
    mail_password = PasswordField("Senha", validators=[DataRequired()])
    mail_default_name = StringField("Nome padrão", validators=[DataRequired()])
    mail_default_email = StringField("E-mail padrão", validators=[DataRequired(), Email()])
    submit = SubmitField("Salvar")
