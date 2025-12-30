from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, SubmitField, FileField, DecimalField
from wtforms.validators import DataRequired, Optional, NumberRange
from flask_wtf.file import FileAllowed, FileRequired

class EntradaForm(FlaskForm):
    tipo_receita = SelectField("Tipo de Receita", choices=[
        ("Dízimo", "Dízimo"),
        ("Oferta", "Oferta"),
        ("Doação", "Doação"),
        ("Evento Beneficente", "Evento Beneficente"),
        ("Aluguel", "Aluguel")
    ], validators=[DataRequired()])
    valor = DecimalField("Valor (R$)", validators=[DataRequired(), NumberRange(min=0)], places=2)
    data = DateField("Data", format='%Y-%m-%d', validators=[DataRequired()])
    descricao = StringField("Descrição", validators=[Optional()])
    conta = SelectField("Conta", choices=[("Caixa", "Caixa"), ("Banco", "Banco")], validators=[DataRequired()])
    submit = SubmitField("Salvar")

class SaidaForm(FlaskForm):
    categoria = SelectField("Tipo de Despesa", choices=[
        ("Manutenção do templo", "Manutenção do templo"),
        ("Contas de consumo", "Contas de consumo"),
        ("Salários", "Salários"),
        ("Materiais", "Materiais"),
        ("Projetos sociais", "Projetos sociais"),
        ("Obras e investimentos", "Obras e investimentos")
    ], validators=[DataRequired()])
    valor = DecimalField("Valor (R$)", validators=[DataRequired(), NumberRange(min=0)], places=2)
    data = DateField("Data", format='%Y-%m-%d', validators=[DataRequired()])
    descricao = StringField("Descrição", validators=[Optional()])
    conta = SelectField("Conta", choices=[("Caixa", "Caixa"), ("Banco", "Banco")], validators=[DataRequired()])
    submit = SubmitField("Salvar")

class FiltroRelatorioForm(FlaskForm):
    inicio = DateField("Início", format='%d-%m-%Y', validators=[Optional()])
    fim = DateField("Fim", format='%d-%m-%Y', validators=[Optional()])
    tipo = SelectField("Tipo", choices=[
        ("", "Todos"),
        ("Entrada", "Entrada"),
        ("Saída", "Saída")
    ], validators=[Optional()])
    categoria = StringField("Categoria", validators=[Optional()])
    submit = SubmitField("Filtrar")

class ComprovanteForm(FlaskForm):
    arquivo = FileField("Comprovante", validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], "Somente imagens ou PDF!")
    ])
    data = DateField("Data", format='%Y-%m-%d', validators=[DataRequired()])
    descricao = StringField("Descrição", validators=[Optional()])
    submit = SubmitField("Upload")
