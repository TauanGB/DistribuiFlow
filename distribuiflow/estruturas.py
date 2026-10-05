"""Estruturas e algoritmos implementados manualmente para o TDE."""


def busca_binaria(lista, codigo):
    """Retorna o índice do objeto com ``codigo`` em uma lista ordenada."""
    inicio, fim = 0, len(lista) - 1
    while inicio <= fim:
        meio = (inicio + fim) // 2
        atual = lista[meio].codigo
        if atual == codigo:
            return meio
        if atual < codigo:
            inicio = meio + 1
        else:
            fim = meio - 1
    return -1


def merge_sort(itens, chave):
    """Devolve uma nova lista estável, ordenada pela função ``chave``."""
    copia = list(itens)
    if len(copia) < 2:
        return copia

    meio = len(copia) // 2
    esquerda = merge_sort(copia[:meio], chave)
    direita = merge_sort(copia[meio:], chave)
    resultado = []
    i = j = 0
    while i < len(esquerda) and j < len(direita):
        if chave(esquerda[i]) <= chave(direita[j]):
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1
    while i < len(esquerda):
        resultado.append(esquerda[i])
        i += 1
    while j < len(direita):
        resultado.append(direita[j])
        j += 1
    return resultado


class PilhaHistorico:
    """Histórico LIFO de pedidos separados."""

    def __init__(self):
        self._itens = []

    def empilhar(self, pedido):
        self._itens.append(pedido)

    def desempilhar(self):
        if not self._itens:
            return None
        return self._itens.pop()

    def listar(self):
        """Retorna cópia do topo para a base, sem alterar a pilha."""
        resultado = []
        for indice in range(len(self._itens) - 1, -1, -1):
            resultado.append(self._itens[indice])
        return resultado


class FilaPrioridade:
    """Heap mínimo de pedidos pendentes, com índice guardado no pedido."""

    _URG = {"alta": 0, "media": 1, "baixa": 2}

    def __init__(self):
        self._itens = []

    @classmethod
    def _chave(cls, pedido):
        return cls._URG[pedido.urgencia], pedido.prazo, pedido.codigo

    def _trocar(self, a, b):
        self._itens[a], self._itens[b] = self._itens[b], self._itens[a]
        self._itens[a].indice_heap = a
        self._itens[b].indice_heap = b

    def _subir(self, indice):
        while indice > 0:
            pai = (indice - 1) // 2
            if self._chave(self._itens[pai]) <= self._chave(self._itens[indice]):
                break
            self._trocar(indice, pai)
            indice = pai

    def _descer(self, indice):
        tamanho = len(self._itens)
        while True:
            esquerda = 2 * indice + 1
            direita = esquerda + 1
            menor = indice
            if esquerda < tamanho and self._chave(self._itens[esquerda]) < self._chave(self._itens[menor]):
                menor = esquerda
            if direita < tamanho and self._chave(self._itens[direita]) < self._chave(self._itens[menor]):
                menor = direita
            if menor == indice:
                break
            self._trocar(indice, menor)
            indice = menor

    def _indice(self, pedido):
        indice = pedido.indice_heap
        if indice is None or indice < 0 or indice >= len(self._itens) or self._itens[indice] is not pedido:
            raise ValueError("pedido não está na fila")
        return indice

    def inserir(self, pedido):
        if pedido.indice_heap is not None:
            raise ValueError("pedido já está em uma fila")
        if pedido.urgencia != "alta" and pedido.urgencia != "media" and pedido.urgencia != "baixa":
            raise ValueError("urgência inválida")
        pedido.indice_heap = len(self._itens)
        self._itens.append(pedido)
        self._subir(pedido.indice_heap)

    def proximo(self):
        return self._itens[0] if self._itens else None

    def retirar_proximo(self):
        if not self._itens:
            return None
        pedido = self._itens[0]
        self.remover(pedido)
        return pedido

    def remover(self, pedido):
        indice = self._indice(pedido)
        ultimo = len(self._itens) - 1
        if indice != ultimo:
            self._trocar(indice, ultimo)
        self._itens.pop()
        pedido.indice_heap = None
        if indice < len(self._itens):
            movido = self._itens[indice]
            self._subir(indice)
            self._descer(movido.indice_heap)
        return pedido

    def atualizar(self, pedido):
        indice = self._indice(pedido)
        if pedido.urgencia != "alta" and pedido.urgencia != "media" and pedido.urgencia != "baixa":
            raise ValueError("urgência inválida")
        self._subir(indice)
        self._descer(pedido.indice_heap)

    def listar_prioridade(self):
        """Retorna pedidos na ordem de atendimento sem modificar o heap."""
        return merge_sort(self._itens, self._chave)
