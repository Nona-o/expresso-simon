# Controller / rotas das paginas do site e comunicação entre views (templates) e models
from flask import render_template, url_for, redirect
from expressosimon import app, database, bcrypt
from expressosimon.models import Usuario, Pedido, Funcionario, Produto, PedidoProduto
from flask_login import login_required, login_user, logout_user, current_user
from expressosimon.forms import (FormLogin, FormCriarConta, FormLoginFuncionario, FormEditarPerfil,
                                 FormAddProduto, FormRemoveProduto, FormLocalEntrega, FormPgtoCartao, FormPedido,
                                 FormEntrega)


@app.route("/inicio")
def inicio():
    return render_template("LoginCadastro/inicio.html")


# caminho do usuario(cliente)


@app.route("/login", methods=["GET", "POST"])
def login():
    form_login = FormLogin()
    if form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=True)
            return redirect(url_for("homepage"))
    return render_template("LoginCadastro/login.html", form=form_login)


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    form_criarconta = FormCriarConta()
    if form_criarconta.validate_on_submit():
        usuarios = Usuario.query.filter_by(email=form_criarconta.email.data).first()
        if usuarios:
            return redirect(url_for("cadastro"))
        else:
            senha = bcrypt.generate_password_hash(form_criarconta.senha.data)
            usuario = Usuario(username=form_criarconta.nome_usuario.data,
                              email=form_criarconta.email.data,
                              senha=senha)
            database.session.add(usuario)
            database.session.commit()
            login_user(usuario, remember=True)
            return redirect(url_for("homepage"))
    return render_template("LoginCadastro/cadastro.html", form=form_criarconta)


@app.route("/")
@login_required
def homepage():
    return render_template("Usuarios/homepage.html")


@app.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    form_editarperfil = FormEditarPerfil()
    form_editarperfil.nome_usuario.data = current_user.username
    form_editarperfil.email.data = current_user.email
    if form_editarperfil.validate_on_submit():
        usuario = current_user
        usuario.username = form_editarperfil.nome_usuario.data
        usuario.email = form_editarperfil.email.data
        database.session.commit()
        return redirect(url_for("perfil"))
    return render_template("Usuarios/perfil.html", usuario=current_user, form=form_editarperfil)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# paginas para os produtos
# função para gerar a lógica de adicionar e remover produtos da sacola
def adicionar_remover(categoria, form_add, form_remove):
    pedidoatual = Pedido.query.filter_by(id_usuario=current_user.id, status="escolhendo produtos").first()
    if form_add.botao_add.data and form_add.validate_on_submit():
        produto = Produto.query.filter_by(id=form_add.id_produto.data).first()
        if pedidoatual is None:
            pedidoatual = Pedido(id_usuario=current_user.id,
                                 status="escolhendo produtos")
            database.session.add(pedidoatual)
            database.session.commit()
            item = PedidoProduto(id_pedido=pedidoatual.id,
                                 id_produto=produto.id)
            database.session.add(item)
            database.session.commit()
            return redirect(url_for(categoria))
        elif pedidoatual.produtos == [] or PedidoProduto.query.filter_by(id_produto=produto.id,
                                                                         id_pedido=pedidoatual.id).first() is None:
            item = PedidoProduto(id_pedido=pedidoatual.id,
                                 id_produto=produto.id)
            database.session.add(item)
            database.session.commit()
            return redirect(url_for(categoria))
        else:
            item = PedidoProduto.query.filter_by(id_produto=produto.id, id_pedido=pedidoatual.id).first()
            item.quantidade = item.quantidade + 1
            database.session.commit()
            return redirect(url_for(categoria))

    if form_remove.botao_remove.data and form_remove.validate_on_submit():
        produto = Produto.query.filter_by(id=form_remove.id_produto.data).first()
        item = PedidoProduto.query.filter_by(id_produto=produto.id, id_pedido=pedidoatual.id).first()
        if pedidoatual is None:
            return redirect(url_for(categoria))
        elif item:
            if item.quantidade == 1:
                database.session.delete(item)
                database.session.commit()
            else:
                item.quantidade = item.quantidade - 1
                database.session.commit()
            return redirect(url_for(categoria))


@app.route("/promocoes", methods=["GET", "POST"])
@login_required
def promocoes():
    form_add = FormAddProduto()
    form_remove = FormRemoveProduto()
    produtos = Produto.query.filter_by(promocao=True).all()
    adicionar_remover("promocoes", form_add, form_remove)
    return render_template("Produtos/promocoes.html", produtos=produtos, form_remove=form_remove,
                           form_add=form_add)


@app.route("/bebidas", methods=["GET", "POST"])
@login_required
def bebidas():
    form_add = FormAddProduto()
    form_remove = FormRemoveProduto()
    produtos = Produto.query.filter_by(categoria="bebidas").all()
    adicionar_remover("bebidas", form_add, form_remove)
    return render_template("Produtos/bebidas.html", produtos=produtos, form_remove=form_remove,
                           form_add=form_add)


@app.route("/paes", methods=["GET", "POST"])
@login_required
def paes():
    form_add = FormAddProduto()
    form_remove = FormRemoveProduto()
    produtos = Produto.query.filter_by(categoria="paes").all()
    adicionar_remover("paes", form_add, form_remove)
    return render_template("Produtos/paes.html", produtos=produtos, form_remove=form_remove,
                           form_add=form_add)


@app.route("/salgados", methods=["GET", "POST"])
@login_required
def salgados():
    form_add = FormAddProduto()
    form_remove = FormRemoveProduto()
    produtos = Produto.query.filter_by(categoria="salgados").all()
    adicionar_remover("salgados", form_add, form_remove)
    return render_template("Produtos/salgados.html", produtos=produtos, form_remove=form_remove,
                           form_add=form_add)


@app.route("/sobremesas", methods=["GET", "POST"])
@login_required
def sobremesas():
    form_add = FormAddProduto()
    form_remove = FormRemoveProduto()
    produtos = Produto.query.filter_by(categoria="sobremesas").all()
    adicionar_remover("sobremesas", form_add, form_remove)
    return render_template("Produtos/sobremesas.html", produtos=produtos, form_remove=form_remove,
                           form_add=form_add)


@app.route("/minhasacola", methods=["GET", "POST"])
@login_required
def minhasacola():
    escolhendo = Pedido.query.filter_by(id_usuario=current_user.id, status="escolhendo produtos").first()
    preparando = Pedido.query.filter_by(id_usuario=current_user.id, status="preparando pedido").first()
    entrega = Pedido.query.filter_by(id_usuario=current_user.id, status="pronto para entrega").first()
    if escolhendo:
        itens = PedidoProduto.query.filter_by(id_pedido=escolhendo.id).all()
        listaprodutos = []
        listaquantidades = []
        preco = 0
        for item in itens:
            produto = Produto.query.filter_by(id=item.id_produto).first()
            listaprodutos = listaprodutos + [produto.nome]
            listaquantidades = listaquantidades + [item.quantidade]
            preco = float(produto.preco) * float(item.quantidade) + preco

        form_endereco = FormLocalEntrega()
        if form_endereco.validate_on_submit():
            escolhendo.endereco = form_endereco.endereco.data
            database.session.commit()
            return redirect(url_for("pagamento"))
        return render_template("usuarios/minhasacola.html", escolhendo=escolhendo,
                               listaprodutos=listaprodutos, listaquantidades=listaquantidades, preco=preco,
                               form=form_endereco)
    elif preparando:
        itens = PedidoProduto.query.filter_by(id_pedido=preparando.id).all()
        listaprodutos = []
        listaquantidades = []
        preco = 0
        for item in itens:
            produto = Produto.query.filter_by(id=item.id_produto).first()
            listaprodutos = listaprodutos + [produto.nome]
            listaquantidades = listaquantidades + [item.quantidade]
            preco = float(produto.preco) * float(item.quantidade) + preco
        return render_template("usuarios/minhasacola.html", escolhendo=escolhendo,
                               listaprodutos=listaprodutos, listaquantidades=listaquantidades, preco=preco,
                               preparando=preparando)
    elif entrega:
        itens = PedidoProduto.query.filter_by(id_pedido=entrega.id).all()
        listaprodutos = []
        listaquantidades = []
        preco = 0
        for item in itens:
            produto = Produto.query.filter_by(id=item.id_produto).first()
            listaprodutos = listaprodutos + [produto.nome]
            listaquantidades = listaquantidades + [item.quantidade]
            preco = float(produto.preco) * float(item.quantidade) + preco
        return render_template("usuarios/minhasacola.html", escolhendo=escolhendo,
                               listaprodutos=listaprodutos, listaquantidades=listaquantidades, preco=preco,
                               preparando=preparando, entrega=entrega)
    elif escolhendo is None or escolhendo.produtos is None:
        return render_template("Usuarios/minhasacola.html", escolhendo=escolhendo,
                               preparando=preparando, entrega=entrega)


@app.route("/pagamento", methods=["GET", "POST"])
@login_required
def pagamento():
    form_pgto = FormPgtoCartao()
    if form_pgto.validate_on_submit():
        usuario = current_user
        usuario.num_cartao = bcrypt.generate_password_hash(form_pgto.num_cartao.data)
        usuario.codigo_cartao = bcrypt.generate_password_hash(form_pgto.num_cartao.data)
        database.session.commit()
        return redirect(url_for("pedidorealizado"))
    return render_template("Usuarios/pagamento.html", form=form_pgto)


@app.route("/pedidorealizado")
@login_required
def pedidorealizado():
    pedidoatual = Pedido.query.filter_by(id_usuario=current_user.id, status="escolhendo produtos").first()
    if pedidoatual:
        pedidoatual.status = "preparando pedido"
        database.session.commit()
    return render_template("Usuarios/pedidorealizado.html")


# caminho funcionario (o logout é a mesma rota que o cliente usa)


@app.route("/login/funcionarios", methods=["GET", "POST"])
def loginfuncionario():
    form_funcionarios = FormLoginFuncionario()
    if form_funcionarios.validate_on_submit():
        funcionario = Funcionario.query.filter_by(login=form_funcionarios.login.data).first()
        if funcionario and bcrypt.check_password_hash(funcionario.senha, form_funcionarios.senha.data):
            login_user(funcionario)
            return redirect(url_for("gerenciarpedidos"))
    return render_template("LoginCadastro/funcionarios.html", form=form_funcionarios)


@app.route("/gerenciarpedidos")
@login_required
def gerenciarpedidos():
    pedidos = Pedido.query.filter_by(status="preparando pedido").all()
    if pedidos:
        return render_template("Funcionarios/gerenciarpedidos.html", pedidos=pedidos)
    else:
        return render_template("Funcionarios/gerenciarpedidos.html", pedidos=pedidos)


@app.route("/entregas")
@login_required
def entregas():
    pedidos = Pedido.query.filter_by(status="pronto para entrega").all()
    if pedidos:
        return render_template("Funcionarios/entregas.html", pedidos=pedidos)
    else:
        return render_template("Funcionarios/entregas.html", pedidos=pedidos)


@app.route("/gerenciarpedidos/detalhespedido/<idpedido>", methods=["GET", "POST"])
@login_required
def detalhespedido(idpedido):
    pedido = Pedido.query.filter_by(id=idpedido).first()
    listaprodutos = []
    if pedido.status == "preparando pedido":
        itens = PedidoProduto.query.filter_by(id_pedido=pedido.id).all()
        listaquantidades = []
        for item in itens:
            produto = Produto.query.filter_by(id=item.id_produto).first()
            listaprodutos = listaprodutos + [produto.nome]
            listaquantidades = listaquantidades + [item.quantidade]
        form_pedido = FormPedido()
        if form_pedido.validate_on_submit():
            pedido.status = "pronto para entrega"
            pedido.id_funcionario = current_user.id
            database.session.commit()
            return redirect(url_for("gerenciarpedidos"))
        return render_template("Funcionarios/detalhespedido.html", pedido=pedido,
                               listaprodutos=listaprodutos, listaquantidades=listaquantidades, idpedido=idpedido,
                               form=form_pedido)
    elif pedido.status == "pronto para entrega":
        localentrega = pedido.endereco
        form_entrega = FormEntrega()
        if form_entrega.validate_on_submit():
            pedido.status = "entregue"
            pedido.id_funcionario = current_user.id
            database.session.commit()
            return redirect(url_for("gerenciarpedidos"))
        return render_template("Funcionarios/detalhespedido.html", pedido=pedido, idpedido=idpedido,
                               form=form_entrega, localentrega=localentrega, listaprodutos=listaprodutos)
