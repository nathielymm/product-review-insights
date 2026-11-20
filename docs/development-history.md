# Progresso do projeto por entregas

Este registro organiza o trabalho em marcos verificáveis. Na auditoria do histórico em 15/11/2026, havia 42 commits locais, nenhum remoto configurado e nenhuma alteração pendente. Isso não é uma contagem de entregas: parte da documentação foi registrada em commits pequenos demais, inclusive aprovações individuais. O histórico original foi preservado; a apresentação abaixo agrupa esses registros por resultado técnico.

## Marcos implementados

As datas são as registradas nos commits originais, sem retroagir ou redistribuir trabalho para aparentar outra cronologia. Os intervalos identificam o primeiro e o último commit do grupo, inclusive.

| Marco | Entrega e evidência | Datas registradas | Commits originais |
|---|---|---|---|
| 1. Ambiente e auditoria | Projeto Python isolado; leitura do Parquet, regras de validade, deduplicação e corpus determinístico com redação heurística. | 24/10/2026 | 2358bcb → a2f7b1a |
| 2. Pipeline RAG local | Embeddings, FAISS, agrupamento temático e geração via Ollama local; correções de deduplicação, paralelismo e citações. | 24/10/2026 | 5bfac8e → 4d8566d |
| 3. Infraestrutura experimental | Execuções pareadas, exportação para anotação com método oculto, registro de configuração/código e documentação acadêmica inicial. | 24/10/2026 | 1bdefa1 → d1bb7c0 |
| 4. Objetivo e unidade de análise | Perfil inicial dos produtos, perguntas voltadas a melhorias e título coerente com análise de avaliações de produtos. | 24/10–08/11/2026 | a787b55 → 1be27a3 |
| 5. Mapeamento dos conjuntos | Cruzamento com catálogo, categorias exploratórias e comparação de candidatos compactos, intermediários e variados. | 08/11/2026 | 9eda8cd → 56d2954 |
| 6. Consistência temática e versões | Inspeção qualitativa rastreável, distinção entre família e versão e proposta dos três estudos de caso. | 08/11/2026 | c1110bc → f21a6b9 |
| 7. Corpora reproduzíveis | Corpus elegível completo, subconjuntos balanceados, desenvolvimento separado e bloqueio de índices de outro conjunto. | 08/11/2026 | 9c6e2a4 → 61aaefa |
| 8. Revisão direcionada dos dados | 20 comentários revisados pela usuária; três exclusões por uso exclusivamente animal; uma assinatura removida; snapshot principal com 3.843 avaliações. | 08/11/2026 | 57cb96c → ad1737e |
| 9. Perguntas de avaliação | Estrutura alinhada de 12 perguntas de análise e duas de controle; referências inicialmente vazias, sem respostas inventadas. | 08/11/2026 | dd7d997 → fad4816 |
| 10. Referência auditada | Matriz de 14 perguntas × cinco famílias em cada conjunto; lacunas e hipóteses explícitas; três pacotes revisados e aprovados. Aprovações não equivalem a referência exaustiva nem denominadores congelados. | 08–15/11/2026 | f16d1b2 → c7a40af |

A referência foi corrigida para representar cada família em cada pergunta; isso é uma decisão metodológica relevante, mantida no registro. As versões anteriores continuam identificadas como históricas. Não é necessário expor cada rodada da conversa para explicar essa melhoria.

## Estado verificável

- Dados principais: 547 avaliações de máscaras para cílios, 1.405 da rotina capilar e 1.891 de funções variadas; total 3.843. Desenvolvimento separado: 625.
- Referências: 210 células de pergunta/família nos três pacotes; interpretações aprovadas pela usuária, sem alegação de revisão humana integral ou independente.
- Última verificação da suíte registrada: 53 testes aprovados. Integração de recuperação realizada no desenvolvimento; isso não mede a qualidade final dos insights.
- Não há avaliação final de cobertura, fidelidade, latência ou custo computacional que permita concluir superioridade de um método.

Os arquivos atuais são indicados por configs/corpus-current.json, configs/benchmark-plan.draft.json e docs/family-reference-matrix-progress.json. Dados, modelos e referências por registro permanecem fora do Git.

## Rubrica e referências para pontuação

Foram preparadas 179 unidades factuais, critérios separados para propostas/controles e a verificação de apoio conhecido nos 27 corpora de sensibilidade. As 58 combinações de pergunta/subconjunto sem âncoras conhecidas ficam explícitas. Ver docs/scoring-rubric.md. Essa é preparação de avaliação, sem resultados dos RAGs ou congelamento final.

## Seleção operacional no desenvolvimento

Foi selecionada uma configuração compartilhada de seis grupos e oito trechos, com teste real local do Gemma 3 4B em três perguntas × dois métodos. Foram preservadas 36 respostas de desenvolvimento; a última rodada passou nas verificações mecânicas, mas a leitura ainda identificou problemas de suporte e inferência. Houve mudança para saída estruturada por família e redução de contexto após falhas no desenvolvimento, sem respostas de avaliação final. Ver docs/development-parameter-selection.md. Isso não demonstra superioridade de método nem qualidade factual garantida.

## Avaliação integrada e regras congeladas

As notas por unidade foram ligadas a respostas e corpora verificáveis, com revisão sem método visível, reaproveitamento de anotações para duplicatas exatas e preservação de falhas. Três índices principais foram preparados e trinta corpora vinculados ao congelamento técnico v1. Conforme decisão da usuária, tempos e tokens substituem o detalhamento de memória/processos. Nenhuma resposta final foi gerada pela preparação. Ver docs/evaluation-freeze.md.

## Geração principal concluída

As 252 tentativas previstas foram executadas sem mudanças no congelamento e sem falhas de chamada. Doze saídas cortadas e com formato inválido foram mantidas. A conferência validou as identidades e vínculos dos três casos completos; os 102 itens de revisão cobrem todos os registros, agrupando apenas quadros exatamente iguais. Tempos e tokens foram preservados, sem monitoramento de memória/processos. Nenhuma anotação de qualidade foi preenchida e a sensibilidade segue pendente. Ver docs/primary-generation.md e docs/primary-generation-summary.json.

## Próximos marcos

1. Concluir README e texto acadêmico com resultados reais; revisar conteúdo antes de criar e enviar ao GitHub privado.

Cada marco poderá conter mais de um commit quando houver entregas independentes. Ajustes locais e aprovações relacionadas serão reunidos na entrega correspondente, em vez de gerar um commit por interação.

## Organização futura do Git

A regra de trabalho está em AGENTS.md. Títulos devem explicar entregas, por exemplo: `feat: add evidence-aware scoring units`, `feat: freeze paired evaluation configuration` ou `docs: report measured experimental results`. Esses são exemplos de entregas futuras, não resultados já alcançados.

Ainda não houve reescrita ou squash dos commits existentes. Antes da primeira publicação, uma eventual consolidação poderá usar os marcos acima como proposta de agrupamento, preservando backup local e rastreabilidade dos commits originais. Não usar squash de todo o projeto em um commit único, nem alterar datas para aparentar progresso diferente do realizado.

## Auditoria humana parcial das respostas

Foi registrada uma amostra reproduzível de 18 itens únicos, seis por conjunto e distribuídos entre tarefas factuais, propostas e controles. As interpretações foram revisadas e aprovadas pela usuária, com correções preservadas, além de cinco itens anteriores de calibração. A pontuação formal começou pelos três controles e permanece incompleta; não há comparação final de qualidade. A revisão é assistida por IA e não independente. Ver docs/human-audit-sampling.md e docs/human-audit-completion.md.

## Anotação formal e métricas principais

Os 102 itens únicos foram anotados pelo assistente e ligados às 252 tentativas, preservando a revisão qualitativa humana parcial e os arquivos originais. Foram registradas 1.568 unidades de afirmação em contexto, apoio de citações, decisões de cobertura e critérios de propostas/controles. As anotações foram seladas antes de revelar comparações; as regras congeladas e as 12 saídas cortadas foram preservadas. O cálculo foi reproduzido com resultado idêntico, e o exportador recusou fichas incompletas e sobrescrita. O temático teve maior fidelidade média nesta anotação, mas sem ganho consistente de cobertura. Não se alega avaliação independente, superioridade geral nem execução da sensibilidade. Ver docs/primary-evaluation-results.v1.md.

## Sensibilidade congelada concluída

Foram executados os 27 cenários, sem seleção posterior de sementes, com 756 tentativas, 756 fichas e 11.876 unidades de afirmação anotadas pelo assistente. Uma falha de chamada, 42 formatos inválidos e 34 cortes foram preservados. As anotações foram seladas antes da comparação; ajustes auxiliares de extração, citações e qualificação de ruído conservaram versões anteriores, sem alterar regras ou denominadores. A exportação foi reproduzida byte a byte e 57 testes passaram. Cobertura e fidelidade não mostraram ganho consistente do temático, que teve medianas de tempo maiores nos nove grupos. A anotação não constitui avaliação humana independente. Ver docs/sensitivity-results.v1.md e docs/sensitivity-validation.v1.json.

## Discussão e conclusões integradas

Os achados principais e de sensibilidade foram incorporados ao resumo, à discussão e às conclusões do README, mantendo a estrutura acadêmica em quatro seções. O texto ampliado em docs/discussion-and-conclusions.v1.md distingue fidelidade, cobertura e utilidade das propostas e preserva as limitações de referência, anotação, amostragem, procedência e recursos. As métricas e o congelamento foram preservados, sem nova execução ou publicação. A redação está preparada para revisão acadêmica.
