from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DecimalField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional

class PatrimonioForm(FlaskForm):
    nome = StringField("Nome*", validators=[DataRequired()])
    descricao = TextAreaField("Descrição", validators=[Optional()])

    categoria = SelectField(
        "Categoria",
        choices=[
            ("Não categorizado", "Não categorizado"),
            ("Móveis", "Móveis"),
            ("Equipamentos", "Equipamentos"),
            ("Imóveis", "Imóveis"),
            ("Veículos", "Veículos"),
        ],
        default="Não categorizado",
        validators=[Optional()]
    )

    numero = StringField("Número", validators=[Optional()])
    valor = DecimalField("Valor", places=2, validators=[Optional()])

    # Aceita tanto dd-mm-aaaa quanto yyyy-mm-dd
    data_entrada = DateField(
        "Data da Entrada",
        format="%d-%m-%Y",
        validators=[Optional()]
    )

    situacao = SelectField(
        "Situação",
        choices=[
            ("Ativo", "Ativo"),
            ("Inativo", "Inativo"),
            ("Manutenção", "Manutenção"),
        ],
        default="Ativo",
        validators=[Optional()]
    )

    submit = SubmitField("Salvar")
