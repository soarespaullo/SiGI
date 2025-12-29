from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

# ===========================
# Formulário da rota: /auth/login
# Usado em login.html
# ===========================
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")


# ===========================
# Formulário da rota: /auth/setup
# Usado quando configuramos o primeiro usuário/admin
# ===========================
class SetupForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Configurar")


# ===========================
# Formulário da rota: /auth/forgot_password
# Usado em forgot_password.html
# ===========================
class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Enviar instruções")


# ===========================
# Formulário da rota: /auth/reset_password/<token>
# Usado em reset_password.html
# ===========================
class ResetPasswordForm(FlaskForm):
    senha = PasswordField("Nova senha", validators=[
        DataRequired(),
        Length(min=6, message="A senha deve ter pelo menos 6 caracteres")
    ])
    confirmar_senha = PasswordField("Confirmar senha", validators=[
        DataRequired(),
        EqualTo("senha", message="As senhas devem coincidir")
    ])
    submit = SubmitField("Redefinir senha")
