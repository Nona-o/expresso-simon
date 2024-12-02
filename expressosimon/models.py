# criar a estrutura do banco de dados
from expressosimon import database, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))


class Usuario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(40), nullable=False)
    email = database.Column(database.String(40), nullable=False, unique=True)
    senha = database.Column(database.String(32), nullable=False)
    num_cartao = database.Column(database.String(19))
    codigo_cartao = database.Column(database.String(4))
    pedido = database.relationship("Pedido", backref="usuario", lazy=True)


class Funcionario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    nome = database.Column(database.String(50), nullable=False)
    login = database.Column(database.String(30), nullable=False)
    senha = database.Column(database.String(32), nullable=False)
    pedido = database.relationship("Pedido", backref="funcionario", lazy=True)


class PedidoProduto(database.Model):
    id_pedido = database.Column(database.Integer, database.ForeignKey('pedido.id'), primary_key=True)
    id_produto = database.Column(database.Integer, database.ForeignKey('produto.id'), primary_key=True)
    quantidade = database.Column(database.Integer, default=1)
    produto = database.relationship("Produto", back_populates="pedidos")
    pedido = database.relationship("Pedido", back_populates="produtos")


class Produto(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    nome = database.Column(database.String(32), nullable=False)
    categoria = database.Column(database.String(20), nullable=False)
    preco = database.Column(database.Numeric(4, 2), nullable=False)
    imagem = database.Column(database.String, default="default.png")
    promocao = database.Column(database.Boolean, default=True, nullable=False)
    pedidos = database.relationship("PedidoProduto", back_populates="produto")


class Pedido(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    data_criacao = database.Column(database.DateTime, default=datetime.now())
    status = database.Column(database.String)
    endereco = database.Column(database.String)
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)
    id_funcionario = database.Column(database.Integer, database.ForeignKey('funcionario.id'))
    produtos = database.relationship("PedidoProduto", back_populates="pedido")

