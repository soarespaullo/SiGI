from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, Length, Optional

class CartaForm(FlaskForm):
    titulo = StringField(
        "Título da Carta",
        validators=[
            DataRequired(message="Informe o título da carta."),
            Length(max=200)
        ]
    )

    # 🔹 Campo para selecionar o membro já cadastrado
    membro_id = SelectField(
        "Membro",
        coerce=int,
        validators=[Optional()],   # ✅ pode deixar opcional se não for obrigatório
        render_kw={"data-placeholder": "Selecione um membro"}
    )

    destinatario = StringField(
        "Destinatário",
        validators=[
            DataRequired(message="Informe o destinatário."),
            Length(max=200)
        ]
    )

    remetente = StringField(
        "Remetente",
        validators=[
            DataRequired(message="Informe o remetente."),
            Length(max=200)
        ]
    )

    cidade = StringField(
        "Cidade",
        validators=[
            DataRequired(message="Informe a cidade."),
            Length(max=100)
        ]
    )

    situacao = SelectField(
        "Situação",
        choices=[
            ("enviado", "Enviado"),
            ("entregue", "Entregue")
        ],
        validators=[DataRequired(message="Informe a situação da carta.")],
        default="enviado"   # ✅ define um valor padrão para não cair em "Rascunho"
    )

    corpo = TextAreaField(
        "Corpo da Carta",
        validators=[
            DataRequired(message="Digite o conteúdo da carta."),
            Length(max=5000)
        ]
    )

    data_emissao = DateField(
        "Data de Emissão",
        format="%Y-%m-%d",
        validators=[Optional()]   # 🔹 não obriga preencher
    )

    submit = SubmitField("Salvar Carta")
