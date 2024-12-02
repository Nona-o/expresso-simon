# criar os formularios do nosso site
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, IntegerField
from wtforms.validators import data_required, Email, EqualTo, Length, ValidationError
from expressosimon.models import Usuario


class FormLogin(FlaskForm):
    email = StringField("E-mail", validators=[data_required(), Email()])
    senha = PasswordField("Senha", validators=[data_required()])
    botao_confirm = SubmitField("Fazer Login")


class FormCriarConta(FlaskForm):
    nome_usuario = StringField("Nome de Usuário", validators=[data_required()])
    email = StringField("E-mail", validators=[data_required(), Email()])
    senha = PasswordField("Senha", validators=[data_required(), Length(6, 20)])
    confirm_senha = PasswordField("Confirmação de Senha", validators=[data_required(), EqualTo("senha")])
    botao_confirm = SubmitField("Criar Conta")

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            return ValidationError("E-mail já cadastrado, faça login para continuar")


class FormLoginFuncionario(FlaskForm):
    login = StringField("Login", validators=[data_required()])
    senha = PasswordField("Senha", validators=[data_required()])
    botao_confirm = SubmitField("Fazer Login")


class FormEditarPerfil(FlaskForm):
    nome_usuario = StringField("Nome de Usuário", validators=[data_required()])
    email = StringField("E-mail", validators=[data_required(), Email()])
    botao_confirm = SubmitField("Salvar alterações")


class FormAddProduto(FlaskForm):
    id_produto = HiddenField()
    botao_add = SubmitField("Adicionar")


class FormRemoveProduto(FlaskForm):
    id_produto = HiddenField()
    botao_remove = SubmitField("Remover")


class FormLocalEntrega(FlaskForm):
    endereco = StringField("Endereço", validators=[data_required()])
    botao_confirm = SubmitField("Ir para pagamento")


class FormPgtoCartao(FlaskForm):
    num_cartao = StringField("Número do Cartão", validators=[data_required(), Length(13, 19)])
    codigo_cartao = StringField("Código de Segurança", validators=[data_required(), Length(3, 4)])
    botao_confirm = SubmitField("Confirmar Compra")


class FormPedido(FlaskForm):
    botao_confirm = SubmitField("Marcar pedido como pronto")


class FormEntrega(FlaskForm):
    botao_confirm = SubmitField("Marcar pedido como entregue")
