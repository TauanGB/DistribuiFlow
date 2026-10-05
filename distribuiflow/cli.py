"""Interface Textual; regras e algoritmos permanecem no ERP."""
from datetime import date
from decimal import Decimal, InvalidOperation
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Horizontal, VerticalScroll
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, Select, Static, TabbedContent, TabPane
from .demo import carregar_demo
from .servico import ERP


def dinheiro(bruto: str) -> int:
    try:
        valor = Decimal(bruto.strip().replace(',', '.'))
        if not valor.is_finite():
            raise ValueError('Informe um valor monetário finito')
        centavos = valor * 100
        if centavos != centavos.to_integral_value():
            raise ValueError('Use no máximo duas casas decimais')
        return int(centavos)
    except InvalidOperation as exc:
        raise ValueError('Informe um valor monetário válido') from exc


def moeda(centavos: int) -> str:
    return f'R$ {centavos // 100},{centavos % 100:02d}'


CLIENTE = [('nome', 'Nome', str), ('telefone', 'Telefone', str)]
PEDIDO = [('cliente_codigo', 'Código do cliente', int), ('descricao', 'Descrição', str),
          ('quantidade', 'Quantidade', int), ('valor_unitario_centavos', 'Valor unitário (R$)', dinheiro),
          ('prazo', 'Prazo (AAAA-MM-DD)', date.fromisoformat), ('urgencia', 'Urgência (alta/media/baixa)', str)]


class DistribuiFlowApp(App):
    TITLE = 'DistribuiFlow — Algoritmos e Estruturas de Dados'
    BINDINGS = [Binding('ctrl+q', 'quit', 'Sair', priority=True),
                Binding('f1', "aba('clientes')", 'Clientes', priority=True),
                Binding('f2', "aba('pedidos')", 'Pedidos', priority=True),
                Binding('f3', "aba('relatorios')", 'Relatórios', priority=True)]
    CSS = '''
    Screen { min-width: 60; }
    #operacoes { height: 3; grid-size: 3; }
    Grid Button { width: 100%; min-width: 1; }
    TabbedContent { height: 1fr; }
    VerticalScroll { padding: 0 1; }
    .formulario { width: 40%; min-width: 30; }
    .cadastro { height: 1fr; }
    .cadastro DataTable { width: 1fr; height: 1fr; margin: 0 1; }
    Input, Select { margin-bottom: 1; }
    .crud { height: 9; grid-size: 2; grid-rows: 3 3 3; }
    DataTable { height: 12; margin-top: 1; }
    #mensagem { height: auto; max-height: 4; padding: 0 1; }
    '''

    def __init__(self, erp: ERP | None = None):
        super().__init__()
        self.erp = erp if erp is not None else ERP()

    def compose(self) -> ComposeResult:
        yield Header()
        with Grid(id='operacoes'):
            yield Button('Carregar demo', id='demo')
            yield Button('Separar próximo', id='separar')
            yield Button('Desfazer', id='desfazer')
        with TabbedContent():
            for entidade, titulo, campos in [('cliente', 'Clientes', CLIENTE), ('pedido', 'Pedidos', PEDIDO)]:
                with TabPane(titulo, id=titulo.lower()):
                    with Horizontal(classes='cadastro'):
                        with VerticalScroll(classes='formulario'):
                            yield Static('Código para consultar/alterar/remover. Na alteração, branco mantém o valor.')
                            yield Label('Código do registro')
                            yield Input(id=f'{entidade}-codigo')
                            for campo, rotulo, _ in campos:
                                yield Label(rotulo)
                                yield Input(id=f'{entidade}-{campo}')
                            with Grid(classes='crud'):
                                for acao in ['cadastrar', 'consultar', 'alterar', 'remover', 'listar', 'limpar']:
                                    yield Button(acao.title(), id=f'{entidade}-{acao}')
                        yield DataTable(id=f't-{entidade}', cursor_type='row', zebra_stripes=True)
            with TabPane('Relatórios', id='relatorios'):
                with VerticalScroll():
                    yield Select([('1 — Geral', 'geral'), ('2 — Filtrar pedidos', 'filtrar'),
                                  ('3 — Fila de prioridade (heap)', 'fila'), ('4 — Histórico (pilha LIFO)', 'historico'),
                                  ('5 — Valor total (Merge Sort)', 'valor')], value='geral', allow_blank=False, id='relatorio')
                    yield Static('Branco ignora o filtro.', id='orientacao-filtros')
                    yield Input(placeholder='Situação: pendente/separado', id='f-status')
                    yield Input(placeholder='Urgência: alta/media/baixa', id='f-urgencia')
                    yield Input(placeholder='Código do cliente', id='f-cliente')
                    yield Button('Exibir relatório', id='exibir')
                    yield Static('', id='titulo-relatorio', markup=False)
                    yield DataTable(id='r-cliente', cursor_type='row', zebra_stripes=True)
                    yield DataTable(id='r-pedido', cursor_type='row', zebra_stripes=True)
        yield Static('Dados apenas em memória. Tab navega; Enter aciona; Ctrl+Q sai.', id='mensagem', markup=False)
        yield Footer()

    def on_mount(self) -> None:
        for prefixo in ('t', 'r'):
            self.query_one(f'#{prefixo}-cliente', DataTable).add_columns('Código', 'Nome', 'Telefone')
            self.query_one(f'#{prefixo}-pedido', DataTable).add_columns(
                'Código', 'Cliente', 'Descrição', 'Qtd', 'Unitário', 'Total', 'Prazo', 'Urgência', 'Situação')
        self.atualizar_cadastros()
        self.atualizar_filtros()
        self.exibir_relatorio()

    def texto(self, campo: str) -> str:
        return self.query_one(f'#{campo}', Input).value.strip()

    def action_aba(self, identificador: str) -> None:
        self.query_one(TabbedContent).active = identificador
        # Não deixa o foco na tabela da aba anterior, que pode reativá-la.
        alvo = {'clientes': 'cliente-codigo', 'pedidos': 'pedido-codigo',
                'relatorios': 'relatorio'}[identificador]
        self.query_one(f'#{alvo}').focus()

    def converter(self, bruto: str, rotulo: str, conversor):
        """Converte a entrada; a validação de negócio continua no ERP."""
        try:
            return conversor(bruto)
        except ValueError as exc:
            formato = ('use um inteiro' if conversor is int else
                       'use AAAA-MM-DD' if conversor == date.fromisoformat else str(exc))
            raise ValueError(f'{rotulo}: {formato}') from exc

    def mensagem(self, texto: str) -> None:
        self.query_one('#mensagem', Static).update(texto)

    def tabela(self, identificador: str, registros: list, entidade: str) -> None:
        tabela = self.query_one(f'#{identificador}', DataTable)
        tabela.clear()
        for r in registros:
            if entidade == 'cliente':
                tabela.add_row(str(r.codigo), Text(r.nome), Text(r.telefone))
            else:
                tabela.add_row(str(r.codigo), str(r.cliente_codigo), Text(r.descricao), str(r.quantidade),
                              moeda(r.valor_unitario_centavos), moeda(r.valor_total_centavos),
                              r.prazo.isoformat(), r.urgencia, r.status)

    def atualizar_cadastros(self) -> None:
        self.tabela('t-cliente', self.erp.listar_clientes(), 'cliente')
        self.tabela('t-pedido', self.erp.listar_pedidos(), 'pedido')
        self.invalidar_relatorio('Dados alterados: clique em Exibir relatório para atualizar.')

    def invalidar_relatorio(self, aviso: str) -> None:
        # Retira resultados antigos para não apresentar dados desatualizados.
        self.query_one('#r-cliente', DataTable).clear()
        self.query_one('#r-pedido', DataTable).clear()
        self.query_one('#titulo-relatorio', Static).update(aviso)

    def atualizar_filtros(self) -> None:
        filtrar = self.query_one('#relatorio', Select).value == 'filtrar'
        for identificador in ('orientacao-filtros', 'f-status', 'f-urgencia', 'f-cliente'):
            self.query_one(f'#{identificador}').display = filtrar

    def on_select_changed(self, evento: Select.Changed) -> None:
        if evento.select.id == 'relatorio':
            self.atualizar_filtros()
            self.invalidar_relatorio('Clique em Exibir relatório para consultar a seleção atual.')

    def exibir_relatorio(self) -> None:
        tipo = self.query_one('#relatorio', Select).value
        clientes = self.erp.listar_clientes() if tipo == 'geral' else []
        if tipo == 'filtrar':
            cliente = self.texto('f-cliente')
            pedidos = self.erp.filtrar_pedidos(status=self.texto('f-status') or None,
                                              urgencia=self.texto('f-urgencia') or None,
                                              cliente_codigo=self.converter(cliente, 'Código do cliente', int) if cliente else None)
        elif tipo == 'fila':
            pedidos = self.erp.fila_prioridade()
        elif tipo == 'historico':
            pedidos = self.erp.historico()
        elif tipo == 'valor':
            pedidos = self.erp.pedidos_por_valor()
        else:
            pedidos = self.erp.listar_pedidos()
        self.query_one('#r-cliente', DataTable).display = tipo == 'geral'
        self.tabela('r-cliente', clientes, 'cliente')
        self.tabela('r-pedido', pedidos, 'pedido')
        self.query_one('#titulo-relatorio', Static).update(
            f'Relatório {tipo}: {len(clientes)} clientes; {len(pedidos)} pedidos. '
            'Fila: atendimento; histórico: topo primeiro; valor: decrescente.')

    def preencher_registro(self, entidade: str, registro) -> None:
        campos = CLIENTE if entidade == 'cliente' else PEDIDO
        self.query_one(f'#{entidade}-codigo', Input).value = str(registro.codigo)
        for campo, _, _ in campos:
            valor = getattr(registro, campo)
            if campo == 'valor_unitario_centavos':
                valor = f'{valor // 100},{valor % 100:02d}'
            elif campo == 'prazo':
                valor = valor.isoformat()
            self.query_one(f'#{entidade}-{campo}', Input).value = str(valor)

    def on_data_table_row_selected(self, evento: DataTable.RowSelected) -> None:
        identificador = evento.data_table.id
        if identificador not in ('t-cliente', 't-pedido'):
            return
        entidade = identificador[2:]
        codigo = int(evento.data_table.get_row(evento.row_key)[0])
        registro = getattr(self.erp, f'consultar_{entidade}')(codigo)
        if registro is not None:
            self.preencher_registro(entidade, registro)
            self.mensagem(f'{entidade.title()} {codigo} selecionado por busca binária.')

    def crud(self, entidade: str, acao: str) -> None:
        campos = CLIENTE if entidade == 'cliente' else PEDIDO
        if acao == 'limpar':
            for campo in ['codigo'] + [c[0] for c in campos]:
                self.query_one(f'#{entidade}-{campo}', Input).value = ''
            self.mensagem('Formulário limpo.')
            return
        if acao == 'listar':
            self.atualizar_cadastros()
            self.mensagem('Cadastros listados por código.')
            return
        codigo = self.converter(self.texto(f'{entidade}-codigo'), 'Código do registro', int) if acao != 'cadastrar' else None
        if acao == 'consultar':
            registro = getattr(self.erp, f'consultar_{entidade}')(codigo)
            if registro is None:
                raise LookupError(f'{entidade} não encontrado')
            self.preencher_registro(entidade, registro)
            self.mensagem(f'{entidade.title()} {codigo} consultado por busca binária.')
            return
        operacao = getattr(self.erp, f'{acao}_{entidade}')
        if acao == 'remover':
            registro = operacao(codigo)
        else:
            valores = {}
            for campo, rotulo, conversor in campos:
                bruto = self.texto(f'{entidade}-{campo}')
                valores[campo] = None if acao == 'alterar' and not bruto else self.converter(bruto, rotulo, conversor)
            registro = operacao(codigo, **valores) if acao == 'alterar' else operacao(**valores)
            if acao == 'cadastrar':
                self.query_one(f'#{entidade}-codigo', Input).value = str(registro.codigo)
        self.atualizar_cadastros()
        self.mensagem(f'Operação {acao} concluída: {entidade} {registro.codigo}.')

    def on_button_pressed(self, evento: Button.Pressed) -> None:
        identificador = evento.button.id or ''
        try:
            if identificador == 'demo':
                carregar_demo(self.erp)
                self.atualizar_cadastros()
                self.mensagem('Demonstração aleatória adicionada: 3 clientes e 6 pedidos; dados anteriores preservados.')
            elif identificador in ('separar', 'desfazer'):
                pedido = self.erp.separar_proximo() if identificador == 'separar' else self.erp.desfazer_ultima_separacao()
                self.atualizar_cadastros()
                self.mensagem(f'Pedido {pedido.codigo}: {pedido.status}.' if pedido else
                              ('Não há pedidos pendentes.' if identificador == 'separar' else 'Histórico vazio.'))
            elif identificador == 'exibir':
                self.exibir_relatorio()
                self.mensagem('Relatório atualizado; nenhuma estrutura foi consumida.')
            elif identificador.startswith(('cliente-', 'pedido-')):
                entidade, acao = identificador.split('-', 1)
                self.crud(entidade, acao)
        except (ValueError, LookupError) as exc:
            self.mensagem(f'Não foi possível concluir: {exc}')


def main() -> None:
    DistribuiFlowApp().run()


if __name__ == '__main__':
    main()
