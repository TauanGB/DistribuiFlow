"""Entidades simples do ERP. Valores monetários são centavos inteiros."""

from dataclasses import dataclass
from datetime import date


@dataclass
class Cliente:
    codigo: int
    nome: str
    telefone: str


@dataclass
class Pedido:
    codigo: int
    cliente_codigo: int
    descricao: str
    quantidade: int
    valor_unitario_centavos: int
    prazo: date
    urgencia: str
    status: str = "pendente"
    indice_heap: int | None = None

    @property
    def valor_total_centavos(self) -> int:
        return self.quantidade * self.valor_unitario_centavos
