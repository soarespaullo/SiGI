from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, Length, Optional

class CertificadoForm(FlaskForm):
    titulo = StringField("Título do Certificado", validators=[DataRequired(), Length(max=200)])
    criado_por = StringField("Nome do Participante", validators=[DataRequired(), Length(max=200)])  # ✅ alinhado com modelo
    evento = StringField("Evento", validators=[DataRequired(), Length(max=200)])
    data_emissao = DateField("Data de Emissão", format="%Y-%m-%d", validators=[Optional()])
    corpo = TextAreaField("Texto do Certificado", validators=[DataRequired()])
    situacao = SelectField(   # ✅ novo campo
        "Situação",
        choices=[
            ("enviado", "Enviado"),
            ("entregue", "Entregue"),
            ("aprovado", "Aprovado")
        ],
        default="enviado",
        validators=[DataRequired()]
    )
    submit = SubmitField("Salvar Certificado")

