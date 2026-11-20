# Interface alinhada à v2

A interface passou a selecionar diretamente GranNaturals, Pure Body Naturals Argan ou Bold Lash, usando os índices individuais e os quatro agrupamentos internos a cada produto. O seletor de conjuntos antigos foi removido. A implementação de demonstração fica em `src/product_review_insights/demo_v2.py`, separada dos arquivos congelados de geração, recuperação e avaliação.

## Comportamento

As seis perguntas de cada produto podem ser selecionadas no formulário. Elas reutilizam o mesmo `prepare_attempt` da execução v2: equivalente inglês, cinco consultas por aspectos, candidatos comuns por RRF, deduplicação e seleção de até oito avaliações. Não foi criado outro algoritmo para simular os métodos no frontend.

Perguntas livres continuam disponíveis. Uma etapa local adicional traduz a pergunta para inglês e propõe cinco consultas por aspectos. Esse planejamento não foi avaliado no experimento e não altera as perguntas congeladas. O servidor rejeita planos estruturalmente inválidos ou com consultas literalmente repetidas; isso não certifica pertinência ou diversidade semântica.

A geração usa o contrato inglês original; somente os campos de apresentação são traduzidos depois, preservando fontes/citações e conferindo que o inglês não mudou. O original pode ser aberto na página. Falha na tradução mantém a resposta inglesa visível; formato inválido e cortes são sinalizados, sem reparo ou repetição automática. A contagem de abrangência considera avaliações únicas efetivamente citadas.

A configuração, bibliotecas registradas, perguntas e implementação reutilizada são conferidas. O índice valida seus arquivos e a identidade do produto; o runtime/modelo local precisa corresponder à v2. O transporte confere o orçamento real de tokens e pode fazer sondagens técnicas separadas, sem escrever nos logs congelados. Uma consulta é processada por vez. Erros de entrada são distintos de falhas de backend no servidor HTTP.

O export `DEMO_SYSTEM` em `scripts/serve_demo.py` foi preservado byte a byte para os pilotos históricos que o importam. A interface v2 não utiliza esse prompt antigo em português.

## Verificações

- 135 testes passaram no ambiente local, incluindo 24 testes da demonstração sobre catálogo, aspectos, deduplicação, isolamento de produto, inglês, tradução, citações, formato inválido, orçamento, bloqueio, erros HTTP e compatibilidade do prompt histórico.
- Os 36 contextos predefinidos foram reconstruídos offline e coincidiram com as fontes/ordem, perguntas inglesas e fingerprints de candidatos do run principal. O comando reproduzível é `scripts/check_demo_v2_contexts.py`; ele não consulta o gerador.
- No navegador, duas consultas reais da pergunta Q1 da GranNaturals foram concluídas, uma por método, com apresentação em português. Foram conferidos links de fonte e contagem de avaliações citadas.
- Uma pergunta livre sobre o aplicador da Bold Lash também concluiu, e seu original inglês foi aberto. Esses testes de uso não entraram nas métricas experimentais.
- Foram reconferidos os hashes dos 73 arquivos congelados e dos 77 arquivos anteriores registrados, além do hash dos agregados publicados.

Os testes mecânicos não certificam fidelidade das respostas nem das traduções. Foi observada imprecisão lexical na apresentação automática de uma consulta da escova; o inglês permaneceu disponível, sem correção silenciosa ou modificação do tradutor experimental. Esse limite não foi tratado como resolvido pela integração.

## Guias e pendências restantes

[local-demo.md](local-demo.md) apresenta o fluxo atual. [reproduction.md](reproduction.md) distingue uso da interface, recálculo com anotações locais e reconstrução a partir da fonte. Não foi certificada instalação em ambiente limpo ou reconstrução integral desde outro Parquet, e os arquivos privados necessários não acompanham o Git/ZIP.

Os itens de integração e guias foram atendidos nesse escopo. Permanecem o fechamento bibliográfico e acadêmico, a procedência do Parquet e as limitações de validação já identificadas. A integração não recalcula qualidade nem modifica resultados congelados.
