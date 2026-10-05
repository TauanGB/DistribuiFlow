# DistribuiFlow

ERP didático de distribuidora, feito para demonstrar **lista, busca binária, pilha, fila de prioridade e Merge Sort** em uma apresentação de Algoritmos e Estruturas de Dados. O programa guarda os dados apenas em memória: ao sair, os cadastros são descartados.

## Executar

Requer Python 3.10 ou mais recente. No terminal, entre nesta pasta e execute:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e .
.\.venv\Scripts\python -m distribuiflow.cli
```

A interface usa **Textual 8.2.8**, fixado em `pyproject.toml`. O comando alternativo é `.\.venv\Scripts\distribuiflow.exe`. Use o Python do ambiente virtual: o Python global pode não ter Textual instalado. Depois da instalação, abra novamente com `.\.venv\Scripts\python -m distribuiflow.cli`. Os algoritmos e regras de negócio não dependem de Textual. A instalação inicial precisa de acesso ao PyPI; o uso não precisa de rede. Recomenda-se terminal com pelo menos 80 colunas e 24 linhas (100 × 35 para apresentar).

Para rodar os testes:

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## Uso

As abas são **Clientes**, **Pedidos** e **Relatórios**. Os botões **Separar próximo**, **Desfazer** e **Carregar demo** ficam no topo. Use mouse ou Tab/Shift+Tab para navegar, Enter para acionar e Ctrl+Q para sair. F1, F2 e F3 abrem Clientes, Pedidos e Relatórios. Os cadastros mostram formulário à esquerda e tabela à direita; na tabela, selecione uma linha e pressione Enter para carregar o registro no formulário. Formulários e tabelas possuem rolagem; as tabelas largas também permitem rolagem horizontal. Nas abas de cadastro, preencha os campos e clique em Cadastrar; o código gerado aparece no formulário. Para Consultar, Alterar ou Remover, informe o código. Consultar preenche o formulário; Limpar apaga os campos. Listar atualiza as tabelas. A carga demonstrativa é opcional; cada acionamento cria três clientes e seis pedidos fictícios com nomes, produtos, quantidades, preços, prazos e urgências aleatórios. Novas cargas acrescentam conjuntos independentes com códigos novos, sem remover dados já existentes. Na aba Relatórios, selecione um dos cinco tipos e clique em **Exibir relatório**. Após mudar os cadastros, os resultados antigos são retirados da tela; clique novamente em Exibir relatório para consultar os dados atuais. O relatório *Fila* mostra a ordem efetiva de atendimento. *Histórico* mostra as separações da mais recente para a mais antiga. *Valor* ordena os pedidos por valor total decrescente.

O prazo é informado como `AAAA-MM-DD`. O valor unitário aceita reais com até duas casas decimais, como `12,50`; internamente, é guardado em centavos inteiros. A urgência aceita `alta`, `media` ou `baixa`. Para alterar um registro, deixe em branco os campos que deseja manter. Os filtros só aparecem quando Filtrar pedidos é selecionado; deixe em branco os filtros que não se aplicam. Trocar o tipo de relatório retira o resultado anterior para evitar confusão.

Clientes com pedidos vinculados não podem ser excluídos. Um pedido separado só pode ser alterado ou excluído depois que sua separação for desfeita. O desfazimento segue a pilha: somente a última separação é revertida. A fila prioriza urgência alta, depois média, depois baixa; em cada nível, o prazo mais próximo vem primeiro e o código menor desempata.

## Estruturas e complexidade

Sejam `c` a quantidade de clientes, `n` a quantidade de pedidos, `p` os pedidos pendentes e `h` o tamanho do histórico. A análise considera a implementação em listas do Python; acréscimo no fim é O(1) **amortizado**, mas uma realocação ocasional pode custar O(n). Os custos abaixo incluem as etapas da função completa, e não apenas da estrutura destacada.

| Função | Custo de tempo | Motivo |
| --- | --- | --- |
| Consultar cliente ou pedido por código | Melhor O(1), pior O(log c) ou O(log n) | Busca binária manual em cadastro ordenado por código. |
| Cadastrar cliente | O(1) amortizado; O(c) numa realocação | Código crescente permite acrescentar ao fim. |
| Cadastrar pedido | O(log c + log p) amortizado; O(n + p) se listas realocarem | Localiza o cliente, acrescenta ao cadastro e insere no heap. |
| Alterar cliente | Melhor O(1), pior O(log c) | Localiza por busca binária; altera campos sem deslocar a lista. |
| Excluir cliente | O(n + c) no pior caso | Verifica pedidos vinculados, localiza o cliente e desloca a lista. |
| Alterar pedido pendente | O(log n + log c + log p) no pior caso | Localiza pedido, valida eventual cliente novo e reajusta sua posição no heap. |
| Excluir pedido pendente | O(n + log p) no pior caso | Localiza e remove do heap, depois desloca a lista de pedidos. |
| Consultar o próximo da fila | O(1) | O heap mantém a maior prioridade na raiz. |
| Separar o próximo | O(log p) amortizado; O(h) numa realocação da pilha | Remove a raiz do heap e empilha o pedido. |
| Desfazer separação | O(log p) amortizado | Desempilha e reinsere o pedido no heap. |
| Filtrar ou listar pedidos | O(n) | Precisa inspecionar ou copiar os pedidos. |
| Exibir histórico | O(h) | Percorre a pilha sem removê-la. |
| Exibir fila em ordem | O(p log p) | A disposição interna de um heap não é uma lista totalmente ordenada. |
| Relatório por valor | O(n log n) em tempo e O(n) em memória | Merge Sort manual sobre cópia; preserva a ordem do cadastro original. |

A análise de melhor caso para busca binária vale quando o código está no ponto médio logo na primeira comparação. Para operações compostas, o melhor caso depende também de quantos registros participam; por exemplo, uma exclusão de cliente ainda precisa verificar vínculos. O roteiro em [APRESENTACAO.md](APRESENTACAO.md) relaciona os conceitos aos passos da demonstração.

## Correspondência com o TDE

| Critério | Onde demonstrar |
| --- | --- |
| CRUD de duas entidades | Abas **Clientes** e **Pedidos**. |
| Lista e busca | Cadastros mantidos por código e consultas por busca binária manual. |
| Pilha LIFO | **Separar próximo**, **Desfazer** e relatório **Histórico**. |
| Fila de prioridade | **Separar próximo** e relatório **Fila**. |
| Ordenação | Relatório **Valor**, implementado com Merge Sort manual. |
| Relatórios | Aba **Relatórios** com listagem geral, filtros, fila, histórico e valor. |
| Análise Big O | Tabela acima e roteiro de apresentação. |

Este trabalho é independente do sistema SpyOffer; nenhum serviço externo, banco de dados ou credencial é necessário.

## Organização e documentação consultada

- `distribuiflow/cli.py`: widgets, conversão de campos e chamadas ao ERP.
- `distribuiflow/demo.py`: geração aleatória de dados, independente da interface, com semente opcional para repetição controlada.
- `distribuiflow/servico.py`: CRUD e regras de negócio, preservados.
- `distribuiflow/estruturas.py`: busca binária, heap, pilha e Merge Sort, preservados.
- `tests/test_interface.py`: testes assíncronos de interação com `App.run_test()` e Pilot, além dos testes existentes.

Referências oficiais consultadas antes da implementação: [Textual 8.2.8 no PyPI](https://pypi.org/project/textual/8.2.8/), [TabbedContent](https://textual.textualize.io/widgets/tabbed_content/), [DataTable](https://textual.textualize.io/widgets/data_table/) e [testes com Pilot](https://textual.textualize.io/guide/testing/). O guia de [testes da tag v8.2.8](https://github.com/Textualize/textual/blob/v8.2.8/docs/guide/testing.md) também foi consultado; as páginas públicas de widgets acompanham a documentação atual. A compatibilidade foi verificada com a versão fixada instalada. Na refatoração, foram consultados os guias oficiais de [abas na tag v8.2.8](https://github.com/Textualize/textual/blob/v8.2.8/docs/widgets/tabbed_content.md) e [entrada e atalhos na tag v8.2.8](https://github.com/Textualize/textual/blob/v8.2.8/docs/guide/input.md).

## Validação da refatoração

Em 05/10/2026, no ambiente virtual do projeto (Windows, Python 3.14, Textual 8.2.8), a instalação editável foi verificada. A versão fixada foi mantida por já estar compatível; foi acrescentado o comando `distribuiflow`. A geração aleatória foi incorporada após a validação descrita abaixo.

Na refatoração da interface Textual, 13 testes passaram e `pip check` não encontrou incompatibilidades. A interface também abriu no terminal, carregou dados demo e encerrou pelo teclado. A nova variação aleatória foi incorporada depois dessa execução; rode os testes descritos acima para verificá-la.

A suíte cobre estruturas e regras do ERP, CRUD completo na interface, erros sem alteração parcial, vínculos, separação/desfazimento, carga repetida, cinco relatórios e redimensionamento. A refatoração acrescenta verificação dos atalhos F1/F2/F3, seleção de registro por Enter, tabela visível em 80 × 24, retirada de relatórios antigos e mensagem de código inválido.

Os testes usam `run_test()` e Pilot: executam os widgets e eventos reais em modo sem terminal. Parte dos campos e seleções é preenchida programaticamente. Isso não equivale a uma revisão visual completa no terminal da sala; confira a legibilidade antes da apresentação.
