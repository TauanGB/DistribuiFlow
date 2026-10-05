"""Regras do ERP independentes da interface de terminal."""

from datetime import date

from .dominio import Cliente, Pedido
from .estruturas import FilaPrioridade, PilhaHistorico, busca_binaria, merge_sort


def _texto(valor: str, campo: str) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} deve ser preenchido")
    return valor.strip()


def _positivo(valor: int, campo: str) -> int:
    if type(valor) is not int or valor <= 0:
        raise ValueError(f"{campo} deve ser um inteiro positivo")
    return valor


def _codigo(valor: int) -> int:
    return _positivo(valor, "código")


def _prazo(valor: date) -> date:
    if type(valor) is not date:
        raise ValueError("prazo deve ser uma data")
    return valor


def _urgencia(valor: str) -> str:
    if valor != "alta" and valor != "media" and valor != "baixa":
        raise ValueError("urgência deve ser alta, media ou baixa")
    return valor


class ERP:
    def __init__(self) -> None:
        self._clientes: list[Cliente] = []
        self._pedidos: list[Pedido] = []
        self._fila = FilaPrioridade()
        self._historico = PilhaHistorico()
        self._proximo_cliente = 1
        self._proximo_pedido = 1

    def consultar_cliente(self, codigo: int) -> Cliente | None:
        _codigo(codigo)
        indice = busca_binaria(self._clientes, codigo)
        return self._clientes[indice] if indice >= 0 else None

    def cadastrar_cliente(self, nome: str, telefone: str) -> Cliente:
        nome, telefone = _texto(nome, "nome"), _texto(telefone, "telefone")
        cliente = Cliente(self._proximo_cliente, nome, telefone)
        self._clientes.append(cliente)
        self._proximo_cliente += 1
        return cliente

    def alterar_cliente(self, codigo: int, *, nome: str | None = None,
                       telefone: str | None = None) -> Cliente:
        cliente = self.consultar_cliente(codigo)
        if cliente is None:
            raise LookupError("cliente não encontrado")
        novo_nome = cliente.nome if nome is None else _texto(nome, "nome")
        novo_telefone = cliente.telefone if telefone is None else _texto(telefone, "telefone")
        cliente.nome, cliente.telefone = novo_nome, novo_telefone
        return cliente

    def remover_cliente(self, codigo: int) -> Cliente:
        cliente = self.consultar_cliente(codigo)
        if cliente is None:
            raise LookupError("cliente não encontrado")
        for pedido in self._pedidos:
            if pedido.cliente_codigo == codigo:
                raise ValueError("cliente possui pedidos vinculados")
        indice = busca_binaria(self._clientes, codigo)
        return self._clientes.pop(indice)

    def consultar_pedido(self, codigo: int) -> Pedido | None:
        _codigo(codigo)
        indice = busca_binaria(self._pedidos, codigo)
        return self._pedidos[indice] if indice >= 0 else None

    def cadastrar_pedido(self, cliente_codigo: int, descricao: str, quantidade: int,
                         valor_unitario_centavos: int, prazo: date, urgencia: str) -> Pedido:
        _codigo(cliente_codigo)
        if self.consultar_cliente(cliente_codigo) is None:
            raise LookupError("cliente não encontrado")
        descricao = _texto(descricao, "descrição")
        quantidade = _positivo(quantidade, "quantidade")
        valor_unitario_centavos = _positivo(valor_unitario_centavos, "valor unitário")
        prazo, urgencia = _prazo(prazo), _urgencia(urgencia)
        pedido = Pedido(self._proximo_pedido, cliente_codigo, descricao, quantidade,
                        valor_unitario_centavos, prazo, urgencia)
        self._fila.inserir(pedido)
        self._pedidos.append(pedido)
        self._proximo_pedido += 1
        return pedido

    def alterar_pedido(self, codigo: int, *, cliente_codigo: int | None = None,
                       descricao: str | None = None, quantidade: int | None = None,
                       valor_unitario_centavos: int | None = None,
                       prazo: date | None = None, urgencia: str | None = None) -> Pedido:
        pedido = self.consultar_pedido(codigo)
        if pedido is None:
            raise LookupError("pedido não encontrado")
        if pedido.status != "pendente":
            raise ValueError("desfaça a separação antes de alterar o pedido")
        novo_cliente = pedido.cliente_codigo if cliente_codigo is None else _codigo(cliente_codigo)
        if self.consultar_cliente(novo_cliente) is None:
            raise LookupError("cliente não encontrado")
        nova_descricao = pedido.descricao if descricao is None else _texto(descricao, "descrição")
        nova_quantidade = pedido.quantidade if quantidade is None else _positivo(quantidade, "quantidade")
        novo_valor = (pedido.valor_unitario_centavos if valor_unitario_centavos is None
                      else _positivo(valor_unitario_centavos, "valor unitário"))
        novo_prazo = pedido.prazo if prazo is None else _prazo(prazo)
        nova_urgencia = pedido.urgencia if urgencia is None else _urgencia(urgencia)
        prioridade_mudou = novo_prazo != pedido.prazo or nova_urgencia != pedido.urgencia
        pedido.cliente_codigo = novo_cliente
        pedido.descricao = nova_descricao
        pedido.quantidade = nova_quantidade
        pedido.valor_unitario_centavos = novo_valor
        pedido.prazo = novo_prazo
        pedido.urgencia = nova_urgencia
        if prioridade_mudou:
            self._fila.atualizar(pedido)
        return pedido

    def remover_pedido(self, codigo: int) -> Pedido:
        pedido = self.consultar_pedido(codigo)
        if pedido is None:
            raise LookupError("pedido não encontrado")
        if pedido.status != "pendente":
            raise ValueError("desfaça a separação antes de remover o pedido")
        self._fila.remover(pedido)
        indice = busca_binaria(self._pedidos, codigo)
        return self._pedidos.pop(indice)

    def separar_proximo(self) -> Pedido | None:
        pedido = self._fila.retirar_proximo()
        if pedido is not None:
            pedido.status = "separado"
            self._historico.empilhar(pedido)
        return pedido

    def desfazer_ultima_separacao(self) -> Pedido | None:
        pedido = self._historico.desempilhar()
        if pedido is not None:
            pedido.status = "pendente"
            self._fila.inserir(pedido)
        return pedido

    def listar_clientes(self) -> list[Cliente]:
        return list(self._clientes)

    def listar_pedidos(self) -> list[Pedido]:
        return list(self._pedidos)

    def filtrar_pedidos(self, *, status: str | None = None, urgencia: str | None = None,
                       cliente_codigo: int | None = None) -> list[Pedido]:
        if status is not None and status not in ("pendente", "separado"):
            raise ValueError("situação deve ser pendente ou separado")
        if urgencia is not None:
            _urgencia(urgencia)
        if cliente_codigo is not None:
            _codigo(cliente_codigo)
        resultado = []
        for pedido in self._pedidos:
            if ((status is None or pedido.status == status)
                    and (urgencia is None or pedido.urgencia == urgencia)
                    and (cliente_codigo is None or pedido.cliente_codigo == cliente_codigo)):
                resultado.append(pedido)
        return resultado

    def fila_prioridade(self) -> list[Pedido]:
        return self._fila.listar_prioridade()

    def historico(self) -> list[Pedido]:
        return self._historico.listar()

    def pedidos_por_valor(self) -> list[Pedido]:
        return merge_sort(self._pedidos, chave=lambda pedido: -pedido.valor_total_centavos)
