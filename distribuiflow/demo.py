"""Geração de dados aleatórios para demonstrações, independente da interface."""
from datetime import date, timedelta
import random

from .servico import ERP


NOMES_CLIENTE = (
    "Mercado", "Empório", "Armazém", "Mercearia", "Distribuidora",
    "Supermercado", "Quitanda", "Atacado",
)
COMPLEMENTOS_CLIENTE = (
    "Sol", "Lua", "Central", "Popular", "do Norte", "Primavera",
    "São José", "Boa Vista", "da Praça", "Estrela",
)
PRODUTOS = (
    "Arroz", "Feijão", "Óleo", "Macarrão", "Açúcar", "Café", "Farinha",
    "Leite", "Biscoito", "Sabão", "Molho de tomate", "Milho",
)


def carregar_demo(erp: ERP, gerador: random.Random | None = None) -> None:
    """Acrescenta três clientes e seis pedidos gerados aleatoriamente.

    ``gerador`` opcional permite reproduzir uma carga em testes ou em aula;
    a interface usa um gerador novo, com semente automática, a cada clique.
    """
    rng = gerador or random.Random()
    clientes = []
    for _ in range(3):
        nome = f"{rng.choice(NOMES_CLIENTE)} {rng.choice(COMPLEMENTOS_CLIENTE)}"
        telefone = f"75{rng.randrange(10**9):09d}"
        clientes.append(erp.cadastrar_cliente(nome, telefone))

    hoje = date.today()
    for _ in range(6):
        cliente = rng.choice(clientes)
        erp.cadastrar_pedido(
            cliente.codigo,
            rng.choice(PRODUTOS),
            rng.randint(1, 30),
            rng.randint(100, 20_000),
            hoje + timedelta(days=rng.randint(1, 30)),
            rng.choice(("alta", "media", "baixa")),
        )
