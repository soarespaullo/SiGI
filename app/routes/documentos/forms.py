from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional

class AtaForm(FlaskForm):
    titulo = StringField("Título da Ata", validators=[DataRequired()])

    # Ajuste: adicionando format="%Y-%m-%d"
    data_reuniao = DateField(
        "Data da Reunião",
        format="%Y-%m-%d",
        validators=[DataRequired()]
    )

    # Novo campo: Tipo da Ata
    tipo = SelectField(
        "Tipo da Ata",
        choices=[
            ("Reunião", "Reunião"),
            ("Fundação", "Fundação"),
            ("Eventos", "Eventos"),
            ("Eleição Diretoria", "Eleição Diretoria"),
            ("Eleição Ministérios", "Eleição Ministérios"),
            ("Outras Reuniões", "Outras Reuniões"),
        ],
        validators=[DataRequired()]
    )

    # Novo campo: Situação da Ata
    situacao = SelectField(
        "Situação da Ata",
        choices=[
            ("Rascunho", "Rascunho"),
            ("Pronto", "Pronto"),
            ("Aprovado", "Aprovado"),
        ],
        default="Rascunho",
        validators=[DataRequired()]
    )

    local = StringField("Local da Reunião", validators=[Optional()])
    presidente = StringField("Presidente da Sessão", validators=[Optional()])
    secretario = StringField("Secretário da Sessão", validators=[Optional()])
    participantes = TextAreaField("Participantes", validators=[Optional()])
    pauta = TextAreaField("Pauta da Reunião", validators=[Optional()])
    deliberacoes = TextAreaField("Deliberações", validators=[Optional()])
    observacoes = TextAreaField("Observações", validators=[Optional()])
    submit = SubmitField("Salvar Ata")
