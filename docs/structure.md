# Estrutura da versão atual

O projeto compara os dois métodos de RAG separadamente em GranNaturals, Pure Body Naturals Argan e Bold Lash. As regras e os resultados experimentais são os da v2 congelada.

| Pasta | Conteúdo atual |
|---|---|
| `configs/` | Receita de preparação local, congelamento, configuração de execução, perguntas, cronograma e rubrica aprovados. |
| `src/product_review_insights/` | Preparação e validação dos dados, recuperação, geração, execução, métricas e integração da interface. |
| `scripts/` | Comandos de preparação, auditoria, execução, relatório, pontuação e interface; dependências reutilizadas pela execução congelada. |
| `demo/` | Página da interface; os nomes dos produtos vêm da configuração aprovada. |
| `tests/` | Testes dos componentes mantidos, com entradas sintéticas e sem executar o modelo. |
| `docs/` | Resultados agregados, discussão, referências, rubrica, verificações técnicas e guias atuais. |

## Por onde começar

- Instalação e interface: [installation.md](installation.md), preparada por `scripts/setup_demo.py` e executada por `scripts/serve_demo.py`.
- Interface com índices experimentais: [local-demo.md](local-demo.md), com a opção `--frozen`.
- Reprodução e recálculo: [reproduction.md](reproduction.md).
- Resultados: [product-evaluation.v2-results.md](product-evaluation.v2-results.md).
- Discussão: [discussion-and-conclusions.v2.md](discussion-and-conclusions.v2.md).
- Critérios: [scoring-rubric.v2-review-proposal.md](scoring-rubric.v2-review-proposal.md); a autoridade é `configs/scoring-rubric.v2.approved.json`.

## Nomes preservados por integridade

Alguns nomes contêm `candidate`, `proposal` ou `not-frozen`. O estado de aprovação/congelamento é definido por `configs/evaluation-freeze.v2.json`, não pelo nome do arquivo. Esses arquivos foram mantidos em seus caminhos e com seus bytes originais para não invalidar os hashes do experimento.

O executor `evaluation_v2.py` importa a busca por aspectos de `scripts/run_product_aspect_pilot.py` e a tradução de `scripts/run_product_original_pilot.py`. Ambos importam `scripts/run_product_pilot.py`, que depende do export `DEMO_SYSTEM` de `scripts/serve_demo.py`. Esses três arquivos de nome histórico continuam sendo dependências da versão atual. Removê-los ou modificar seu conteúdo exigiria uma migração separada, sem apresentar o código modificado como a execução congelada.

`study.py` é usado na validação dos índices por `retrieval.py` e importa utilitários de amostragem de `diversity.py`; por isso ambos permanecem no pacote.

## Arquivos locais

`data/`, `artifacts/` e `results/` contêm insumos e saídas privados, ignorados pelo Git. Não acompanham o repositório e continuam necessários conforme a tarefa descrita no guia de reprodução. `.venv/` contém o ambiente Python local. Os comandos de uso estão em `scripts/`; não há um comando de terminal adicional com padrões de experimentos anteriores.

## Verificação da estrutura atual

A suíte mantida tem 85 testes, aprovados no ambiente original e em um ambiente virtual novo. A instalação independente baixou a fonte pública e construiu índices próprios; seis consultas reais, uma por produto e método, foram verificadas. Consulte o [registro de instalação](local-install-validation.json) para versões e limites da verificação.

Na integração com os insumos experimentais, os 36 contextos predefinidos coincidiram com os registrados, sem chamadas ao gerador. Os 73 arquivos vinculados ao congelamento foram conferidos, e o recálculo das métricas coincidiu integralmente com os agregados publicados. Esses testes verificam funcionamento e integridade; não ampliam a validação semântica.

As contagens maiores nos relatórios técnicos anteriores descrevem as suítes existentes naquelas verificações. Os registros congelados não foram reescritos para substituir esses números pela contagem da suíte atual.
