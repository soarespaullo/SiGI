from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FileField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class EditarPerfilForm(FlaskForm):
    nome = StringField(
        "Nome",
        validators=[DataRequired(message="O nome é obrigatório.")]
    )

    email = StringField(
        "Email",
        validators=[DataRequired(message="O email é obrigatório."), Email()]
    )

    foto = FileField("Foto de Perfil")  # pode adicionar FileAllowed se quiser restringir a imagens

    ativo = SelectField(
        "Status",
        choices=[("1", "Ativo"), ("0", "Inativo")],
        validators=[DataRequired(message="Selecione o status.")]
    )

    role = SelectField(
        "Nível",
        choices=[("admin", "Administrador"), ("user", "Usuário")],
        validators=[DataRequired(message="Selecione o nível.")]
    )

    submit = SubmitField("Salvar")

class AlterarSenhaForm(FlaskForm):
    senha_atual = PasswordField(
        "Senha Atual",
        validators=[DataRequired(message="Informe sua senha atual.")]
    )
    nova_senha = PasswordField(
        "Nova Senha",
        validators=[
            DataRequired(message="Informe a nova senha."),
            Length(min=6, message="A nova senha deve ter pelo menos 6 caracteres.")
        ]
    )
    confirmar_senha = PasswordField(
        "Confirmar Nova Senha",
        validators=[
            DataRequired(message="Confirme a nova senha."),
            EqualTo("nova_senha", message="As senhas não coincidem.")
        ]
    )
