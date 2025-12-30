from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Optional, Length

class EventoForm(FlaskForm):
    titulo = StringField("Título", validators=[DataRequired(), Length(max=100)])
    descricao = TextAreaField("Descrição", validators=[Optional(), Length(max=500)])
    
    tipo = SelectField("Tipo", choices=[
        ("culto", "Culto"),
        ("reuniao", "Reunião"),
        ("conferencia", "Conferência"),
        ("outro", "Outro")
    ], validators=[DataRequired()])
    
    data_inicio = DateTimeLocalField(
        "Data/Hora Início",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired()]
    )
    
    data_fim = DateTimeLocalField(
        "Data/Hora Término",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired()]
    )
    
    local = StringField("Local", validators=[Optional(), Length(max=200)])
    organizador = StringField("Organizador", validators=[Optional(), Length(max=100)])
    
    status = SelectField("Status", choices=[
        ("ativo", "Ativo"),
        ("cancelado", "Cancelado"),
        ("concluido", "Concluído")
    ], validators=[DataRequired()])
    
    submit = SubmitField("Salvar")
