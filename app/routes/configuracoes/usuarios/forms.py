from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, Length, Optional

class NovoUsuarioForm(FlaskForm):
    nome = StringField(
        "Nome",
        validators=[DataRequired(message="Informe o nome"), Length(min=3, max=50)]
    )
    email = StringField(
        "Email",
        validators=[DataRequired(message="Informe o email"), Email(message="Email inválido")]
    )
    senha = PasswordField(
        "Senha",
        validators=[DataRequired(message="Informe a senha"), Length(min=6, message="A senha deve ter pelo menos 6 caracteres")]
    )
    role = SelectField(
        "Papel",
        choices=[("admin", "Administrador"), ("user", "Usuário")],
        validators=[DataRequired(message="Selecione o papel")]
    )
    ativo = SelectField(
        "Status",
        choices=[("true", "Ativo"), ("false", "Inativo")],
        validators=[DataRequired(message="Selecione o status")]
    )
    foto = FileField("Foto de Perfil")  # 🔹 novo campo
    submit = SubmitField("Criar Usuário")


class EditarUsuarioForm(FlaskForm):
    nome = StringField(
        "Nome",
        validators=[DataRequired(message="Informe o nome"), Length(min=3, max=50)]
    )
    email = StringField(
        "Email",
        validators=[DataRequired(message="Informe o email"), Email(message="Email inválido")]
    )
    senha = PasswordField(
        "Senha (opcional)",
        validators=[Optional(), Length(min=6, message="A senha deve ter pelo menos 6 caracteres")]
    )
    role = SelectField(
        "Papel",
        choices=[("admin", "Administrador"), ("user", "Usuário")],
        validators=[DataRequired(message="Selecione o papel")]
    )
    ativo = SelectField(
        "Status",
        choices=[("true", "Ativo"), ("false", "Inativo")],
        validators=[DataRequired(message="Selecione o status")]
    )
    foto = FileField("Foto de Perfil")  # 🔹 novo campo
    submit = SubmitField("Salvar Alterações")
