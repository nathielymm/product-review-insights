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

## Interface demonstrativa local

Foi adicionada uma interface de pergunta, seleção de método, resposta e fontes sobre o pipeline existente, com seleção dos três conjuntos principais. O serviço é restrito ao loopback e não grava consultas nem altera experimentos. Testes verificam validação das entradas, seleção do método, exposição somente das evidências incluídas e liberação após falha. A suíte passou com 59 testes, e os dois métodos foram conferidos no navegador com geração real local, incluindo abertura de fonte citada. O ambiente e os arquivos experimentais congelados foram preservados. Instruções em docs/local-demo.md.

## Respostas em português na demonstração

A interface passou a usar um contrato próprio de geração em português brasileiro, mantendo fontes originais em inglês, identificadores e validação de citações. O código e os prompts experimentais congelados foram preservados. Uma consulta real confirmou o idioma e oito fontes no contexto; isso não constitui validação semântica da resposta. A suíte passou com 60 testes, incluindo isolamento do prompt e preservação das fontes.

## Identificação descritiva dos produtos na interface

As 15 famílias passaram a ser apresentadas por tipo e nome descritivo do mapeamento existente, mantendo códigos e grupos como referências secundárias. Os rótulos são exclusivos da apresentação, sem alterar prompt, busca ou experimentos. A interface explicita a ausência de confirmação de versão/fórmula. A suíte passou com 61 testes; a cobertura inclui as 15 famílias e a preservação dos identificadores e do conteúdo enviado ao modelo.

## Simplificação dos textos da interface

Foram removidos o rótulo de demonstração local, o rodapé explicativo e orientações repetitivas. A explicação dos métodos e os estados de consulta foram simplificados, mantendo fontes acessíveis e avisos de falha ou resposta incompleta. Mudança apenas de apresentação, sem nova geração ou alteração experimental.

## Respostas organizadas por produto

A apresentação passou a usar cartões por família com relatos, fontes, sugestões e pontos de verificação separados, preservando campos e citações do modelo. Saídas fora do formato mantêm o texto original. A suíte passou com 62 testes, incluindo o transporte dos achados sem reescrita. Nenhum prompt ou experimento congelado foi alterado.

## Abrangência das fontes citadas

Foi adicionado um resumo de avaliações únicas e produtos efetivamente citados, deduplicando trechos da mesma avaliação e excluindo fontes não citadas. Saídas sem estrutura confiável não exibem contagem presumida. A suíte passou com 63 testes; experimentos e prompts foram preservados.

## Consulta individual por família na interface

Foi adicionado um seletor por produto com opções vinculadas ao conjunto. A busca individual restringe os vetores candidatos antes do ranking, utilizando um índice somente em memória e os agrupamentos existentes. Permanecem a consulta geral, os dois métodos e o orçamento de oito trechos. A suíte passou com 65 testes, incluindo exclusão de outras famílias antes do ranking e rejeição de seleção incompatível. Duas consultas reais, uma por método, retornaram oito fontes exclusivamente da família selecionada e formato válido. A extensão não altera experimentos nem estabelece ganho de profundidade sem avaliação adicional.

## Proposta de metodologia v2 por família

Foi preparada docs/methodology-v2-proposal.md para alinhamento: comparação pareada dentro de uma família, agrupamentos locais, desenvolvimento separado e avaliação de profundidade por aspectos, condições e contrastes sustentados. A grade proposta de 540 tentativas depende de piloto e novo congelamento. A v1 e sua discussão permanecem preservadas; não há geração ou resultado v2 nesta entrega.

## Auditoria de identidade e rascunhos por item

Foram auditadas as 15 famílias existentes por códigos de item e metadados locais: 19 ASINs nas 3.843 avaliações elegíveis, com três famílias de múltiplos itens. A inspeção de relatos encontrou ambiguidades de versão mesmo sob um único código. Foram preparados 19 casos privados em destinos novos com linhagem preservada e sem certificação de homogeneidade ou novos agrupamentos. Cinco candidatos receberam prioridade de revisão, sem fixar recorte final. Relatórios públicos contêm apenas agregados; a suíte passou com 66 testes. Ver docs/product-identity-audit.v1.md.

## Critério de produto sem exclusão por reformulação

A metodologia foi corrigida para permitir versões, mudanças de fórmula/aplicador, tamanhos e kits do mesmo produto, com atribuição e incerteza preservadas. A revisão inclui novamente todos os 15 candidatos; o mapeamento em configs/product-focused-scope.draft.json cobre 3.784 avaliações sem sobreposição. Outras 59 avaliações do item B01D6O4Y12 ficam preservadas por identidade funcional pendente, não por reformulação. A quantidade final de produtos e a grade experimental permanecem abertas ao piloto. Contagens e hashes anteriores foram conferidos; não houve geração, alteração dos corpora antigos ou ativação do novo mapeamento. Ver docs/product-scope-revised.md.

## Piloto individual Curly Co. com agrupamentos locais

Foram construídos quatro agrupamentos exploratórios somente nas 804 avaliações (805 trechos) do difusor e executadas duas perguntas nos dois métodos, com orçamento comum e uma tentativa por combinação. As quatro saídas tiveram formato válido e não foram cortadas, mas a leitura das fontes encontrou erros de atribuição/causalidade e omissão de reclamações na geração. Os candidatos de ambas as perguntas alcançaram apenas dois grupos; os contextos eram idênticos na primeira pergunta e tinham sete trechos comuns na segunda. O relatório não declara ganho de profundidade ou vencedor. O caso é desenvolvimento, os agregados são reproduzíveis e 68 testes passaram. Ver docs/curly-product-pilot.v1.md. Os experimentos congelados permanecem preservados.

## Segunda rodada Curly Co.: busca por aspectos e achados curtos

Foram executadas quatro novas tentativas em destinos separados, com cinco buscas por aspectos, fusão de candidatos comum aos métodos e deduplicação por avaliação. A P01 alcançou quatro grupos nos candidatos; a P02 permaneceu em dois. O contrato de achados curtos exigiu uma fonte e trecho literal por achado, mas as quatro saídas foram rejeitadas por pelo menos um trecho não literal; as duas respostas P01 também vieram em inglês. Foram preservadas, sem reparo, tradução ou nova tentativa. A revisão qualitativa documenta melhorias de inspecionabilidade e problemas persistentes de sentido, classificação e atribuição; não há vencedor ou escore final de profundidade. Os 29 arquivos anteriores registrados passaram na conferência de preservação, os agregados foram reproduzidos e 73 testes passaram. Ver docs/curly-product-pilot.v2-comparison.md.

## Terceira rodada Curly Co.: geração simplificada e fontes do sistema

Foram executadas quatro respostas com prompt e esquema em português, removendo a exigência de cópia de trechos e campos extras. As fontes foram anexadas pelo sistema a partir do contexto original. Os contextos e candidatos coincidiram exatamente com a segunda rodada, e as quatro saídas tiveram formato válido, português e ausência de corte/falha. A revisão qualitativa ainda encontrou atribuição errada de condições e partes, propostas mal vinculadas a elogios e causalidade mais forte que a fonte. Não há declaração de fidelidade resolvida ou vencedor. Os 38 arquivos anteriores registrados foram preservados, os agregados foram reproduzidos e 78 testes passaram. Ver docs/curly-product-pilot.v3-comparison.md. A interface não foi promovida automaticamente para esta configuração de desenvolvimento.

## Quarta rodada Curly Co.: geração isolada por fonte

Foram compostas quatro respostas a partir de 32 chamadas independentes, cada uma com uma avaliação e fonte fixada pelo sistema. Os candidatos e contextos coincidiram com a terceira rodada; o teto agregado de saída permaneceu em 1.536 tokens por resposta, distribuído em 192 por fonte. As 32 chamadas tiveram formato válido e não foram cortadas por tokens, mas a revisão encontrou erros de identidade dentro da fonte, inversão de dobrado/desdobrado, causalidade mal qualificada, placeholders e frases incompletas no limite de caracteres. Houve correção pontual da proposta de fixação cabeça-corpo. A entrada cresceu de 5.917 para 19.115 tokens; o resultado não é ganho de qualidade comprovado. Foram preservados os 46 arquivos anteriores registrados, reproduzidos os agregados e aprovados 83 testes. Ver docs/curly-product-pilot.v4-comparison.md.

## Quinta rodada Curly Co.: frases completas e referente do produto

Foram ampliados os limites de caracteres e acrescentado um referente atual/anterior/incerto, mantendo fontes, 32 chamadas isoladas e teto de saída da quarta rodada. As saídas ficaram sem os fragmentos interrompidos antes observados, mas a revisão ainda encontrou inversão de dobrado/desdobrado, falha antiga atribuída ao produto atual e suspeitas inventadas de fabricação/uso excessivo. Todos os rótulos foram produto_atual, o que não validou identidade. O objetivo semântico não foi atingido; não houve promoção à interface. Foram preservados 56 arquivos anteriores, reproduzidos os agregados e aprovados 85 testes antes da execução. Ver docs/curly-product-pilot.v5-comparison.md.

## Sexta rodada Curly Co.: gerador original inglês e tradução de apresentação

A função generation.generate e seu prompt/contrato inglês originais foram usados diretamente, com uma geração por pergunta/método. Os mesmos contextos da rodada 5 e os grupos internos do produto foram preservados. Quatro traduções separadas afetaram apenas textos de apresentação, mantendo inglês, fontes e citações. As oito chamadas passaram no formato e não tiveram corte, mas a revisão distinguiu erros de geração já no inglês de erros léxicos introduzidos na tradução. Não houve declaração de fidelidade resolvida ou mudança de modelo. Foram verificados 65 arquivos anteriores, reproduzidos os agregados e aprovados 91 testes. Ver docs/curly-product-pilot.v6-comparison.md.

## Revisão de vínculos do piloto individual

As quatro respostas da rodada 7 repetiram exatamente o inglês e os contextos da rodada 6. A revisão do assistente cobriu 53 frases e confirmou erros de atribuição, certeza e referente. As 14 auditorias do mesmo modelo foram rejeitadas por rótulos incompatíveis; o alinhamento por embeddings ficou apenas como auxílio à inspeção. Nenhuma referência ou resposta foi corrigida silenciosamente. A auditoria não será promovida; o congelamento final depende da rubrica e da grade experimental, sem exigir ausência total de erros para comparar métodos. Os 74 arquivos anteriores registrados foram preservados. Ver docs/curly-product-pilot.v7-comparison.md.

A suíte final passou com 97 testes, incluindo rejeição de aceitação contraditória e deduplicação de candidatos por avaliação. Agregados reproduzidos byte a byte; importação do encoder adiada para evitar carregá-lo em testes puramente determinísticos.

## Perguntas específicas para avaliação por produto — proposta

A leitura dirigida dos corpora GranNaturals (613 avaliações), Pure Body Naturals (473) e Bold Lash (123) embasou quatro questões específicas por produto, uma síntese de oportunidades e um controle de limites comerciais. As âncoras individuais foram registradas somente em results/; não constituem referência exaustiva ou aprovada. O rascunho mantém 36 respostas principais propostas e distingue aplicação, desempenho, condição da unidade e comparações entre compras. Não houve geração, ativação da configuração ou congelamento. Ver docs/product-questions.v2-review-proposal.md.

## Referência do produto GranNaturals consolidada

Após revisão dos seis blocos, foram consolidados 20 comentários com tradução/interpretação, cinco itens de síntese e um controle de limites comerciais. A ficha tem 26 itens aprovados, com fontes e cadeia de aprovações verificadas; conteúdo individual permanece somente nos arquivos locais ignorados. Uma divergência de tradução entre rascunho e apresentação aprovada foi reconciliada explicitamente, preservando os arquivos anteriores. A referência é parcial e não congela denominadores, rubrica ou experimento. Não houve geração nova. Ver docs/grannaturals-reference-summary.v2.md.

## Referência do shampoo Pure Body Naturals consolidada

Os seis blocos aprovados foram consolidados em uma ficha por produto: 20 comentários com tradução/interpretação, cinco itens de síntese e um controle sobre vendas. Foram conferidos os textos originais, hashes das aprovações e integridade dos 26 itens. A referência da GranNaturals permanece preservada e o registro local aponta para ambas as fichas. Conteúdo individual fica somente em arquivos ignorados; o Git contém apenas protocolo e resumo agregado. A referência é parcial, sem denominadores ou experimento congelados, e não houve geração nova. Ver docs/pure-body-naturals-reference-summary.v2.md.

## Referência da Bold Lash e ciclo dos três produtos consolidados

Os seis blocos da Bold Lash foram consolidados após aprovação: 20 comentários com tradução/interpretação, cinco itens de síntese e um controle de limites comerciais. Foram conferidos textos, vínculos, hashes e igualdade dos 26 itens aprovados. As fichas da GranNaturals e Pure Body Naturals permanecem preservadas. O ciclo contém três referências parciais, 18 casos produto/pergunta e 78 itens administrativos de papéis distintos, sem pendência nos blocos apresentados; isso não estabelece cobertura exaustiva, avaliação independente ou denominadores. Fontes e anotações individuais continuam somente em arquivos locais ignorados. Rubrica quantitativa e protocolo comum ainda precisam ser finalizados antes do congelamento; não houve geração nova. Ver docs/bold-lash-reference-summary.v2.md e docs/product-reference-progress.v2.json.

## Proposta de rubrica e denominadores para revisão

Foi preparada uma proposta separada para as três referências por produto: 55 alvos de conteúdo, 38 de condições/qualificações e 16 de contrastes por método, distribuídos em 12 casos Q1–Q4. Propostas são avaliadas em Q1–Q5 (15 casos por método) e controles em Q6 (três), com fidelidade/citações por afirmação, tratamento explícito de falhas, agregação por produto e tradução separada. Os vínculos dos 109 alvos propostos foram conferidos contra itens revisados; matrizes individuais ficam somente no armazenamento local. A divisão e a pontuação ainda aguardam aprovação e implementação: nenhuma métrica foi calculada, configuração congelada ou geração final executada. A grade de 36 respostas principais e 24 repetições diagnósticas permanece proposta. Ver docs/scoring-rubric.v2-review-proposal.md.

## Rubrica aprovada e configuração v2 preparada para revisão

A aprovação da rubrica, unidades e denominadores foi registrada em uma versão nova, mantendo a proposta anterior. Foi preparada a configuração candidata dos três produtos, com 18 equivalentes ingleses, 90 buscas por aspectos e ordem balanceada de 36 tentativas principais e 24 diagnósticas; tradução separada prevista para até 36 respostas principais. Três índices locais foram construídos, e 36 contextos foram conferidos sem execução de LLM: oito avaliações por contexto, sem mistura de produtos; sete pares tiveram o mesmo conjunto de fontes. Índices, unidades e contextos individuais ficam ignorados; apenas parâmetros e agregados são versionados. Orçamento real de tokens, runtime ativo, revisão dos grupos/aplicabilidade, calibração e implementação/verificação da execução/métricas v2 permanecem pendentes antes do congelamento. Nenhuma geração final ou congelamento foi realizado. Ver docs/evaluation-configuration.v2-review.md.

## Execução e métricas v2 implementadas, sem congelamento

A aprovação da configuração foi registrada sem liberar gerações finais. O runtime/digest local foi conferido; 36 contextos e uma checagem na janela final usaram sondagens de um token. A maior entrada mais a reserva de saída foi 3.327/8.192 tokens. Foram verificados os 60 comentários de referência nos trechos e documentados seis exemplos de calibração Curly Co. e a inspeção dos 12 agrupamentos, com sobreposição preservada. O novo executor exige congelamento autorizado, guarda contexto/tokens e preserva erros/saídas; o motor de métricas valida anotações completas e exporta somente agregados públicos. A suíte passou com 119 testes (22 novos da v2), incluindo execução sintética completa e denominadores de falhas. As métricas semânticas dependem das futuras anotações; não houve respostas finais, métricas reais da v2 ou congelamento. Ver docs/product-evaluation.v2-implementation.md.

## Configuração v2 congelada e geração concluída

Após autorização, foi selado um manifesto com 73 arquivos de entrada, código e verificações técnicas. A grade executou 36 respostas principais e 24 diagnósticas em inglês, além das 36 traduções separadas: todas passaram no formato, sem erros de execução ou cortes de tokens. Não houve reparo, repetição extra ou escolha da melhor resposta. Os hashes confirmaram a preservação do inglês, dos 73 arquivos congelados e de 77 arquivos anteriores. Respostas e fontes individuais permanecem ignoradas; o Git registra apenas manifesto, ferramenta de conferência e agregados. A anotação semântica e a revisão humana parcial planejada ainda estão pendentes; formato válido não comprova fidelidade ou superioridade. Ver docs/product-evaluation.v2-generation.md.

## Anotação da v2 e pacotes de revisão preparados

As 36 respostas principais receberam anotação do assistente em fichas com métodos ocultos, validada estruturalmente pelo motor congelado. Foram mantidos alvos e regras, com posições exatas no inglês, deduplicação e justificativas de fontes alternativas. A amostra previamente definida foi convertida em 12 pacotes de revisão humana, sem seleção por qualidade. Nenhum item está aprovado nesta etapa e nenhuma métrica semântica foi publicada; a avaliação continua assistida e parcialmente revisada, sem independência. Inglês, traduções experimentais, 73 arquivos congelados e 77 arquivos anteriores foram reconferidos sem mudanças. Ver docs/product-evaluation.v2-annotation-review.md.

## Revisão humana parcial e métricas da v2 concluídas

Os 12 itens da amostra predefinida tiveram suas interpretações aprovadas, com recibos vinculados às fontes e sem alterações dos rótulos. Após essa etapa, os métodos foram identificados para exportar as métricas dos 36 casos pelo motor congelado; o recálculo dos agregados e casos coincidiu com a exportação. A cobertura média de conteúdo favoreceu o temático (18,75% contra 12,50%), enquanto a fidelidade média favoreceu o tradicional (85,33% contra 80,95%). Qualificações completas ficaram sem crédito nas respostas de ambos e contrastes tiveram 8,33%; não há vencedor uniforme nem nota global. Controles reconheceram os limites comerciais, mas falharam no critério de premissas sem erro. A revisão é parcial e assistida, sem independência; os seis diagnósticos textualmente diferentes continuam fora do cálculo principal e aguardam inspeção separada. Foram preservados os 73 arquivos congelados e os 77 arquivos anteriores registrados, sem nova geração. Ver docs/product-evaluation.v2-results.md.

## Discussão e conclusões por produto integradas para revisão

O README acadêmico passou a apresentar o recorte individual de três produtos, os denominadores e os resultados reais da v2, mantendo Introdução, Modelagem, Resultados e Conclusões e identificação acadêmica em branco. Foi criado um texto ampliado próprio de discussão/conclusões, sem misturar denominadores ou percentuais de outros desenhos. A análise explicita maior cobertura temática na resposta e maior fidelidade média tradicional, as lacunas em qualificações/contrastes/propostas e a ausência de utilidade decisória validada. Foram mantidos os limites de referência parcial, revisão humana não independente, procedência, identidade de produtos, recursos locais e inspeção diagnóstica pendente. Os arquivos e resultados anteriores permanecem preservados; não houve nova geração ou pontuação. Texto sujeito à revisão da usuária. Ver docs/discussion-and-conclusions.v2.md.

## Inspeção separada das seis diferenças diagnósticas concluída

A aprovação da discussão/conclusões foi registrada e as seis saídas diferentes foram comparadas ao principal e às fontes, sem novas gerações ou pontuação das repetições. Contextos e requisições ao modelo coincidiram nos seis pares. Foram verificadas três comparações distintas, cada uma repetida duas vezes: mudanças de achados/propostas, paráfrase com atribuição mais firme nos limites e alterações nas ressalvas/foco de investigação. Houve melhorias locais junto a problemas novos ou persistentes, sem inferir ganho global ou estabilidade semântica. Métricas, anotações e respostas principais permaneceram iguais; conferidos os 73 arquivos congelados e os 77 anteriores registrados. A versão aprovada do texto foi preservada, e a documentação corrente teve apenas a atualização diagnóstica e de pendência. Ver docs/product-evaluation.v2-diagnostic-inspection.md.

## Revisão final de coerência documentada

A revisão confrontou README, resultados, configuração, reprodução e interface. Os 119 testes passaram; o recálculo dos 36 casos coincidiu com os agregados publicados e os hashes dos 73 arquivos congelados e 77 anteriores foram conferidos. A inspeção do formulário no navegador confirmou que a interface ainda usa conjuntos/índices anteriores; código e testes também mantêm busca sem aspectos e geração direta em português. Foram documentados os ajustes de integração v2, atualização dos guias/testes e fechamento bibliográfico, sem modificar esses comportamentos nesta etapa ou executar o Gemma. Servidor temporário encerrado; nenhuma mudança nos resultados congelados. Ver docs/final-coherence-review.v2.md.

## Interface e guias alinhados à v2

A demonstração passou aos três índices individuais e ao helper de aspectos/RRF da v2. Perguntas avaliadas reutilizam suas entradas congeladas; perguntas livres têm planejamento local separado, sem compor métricas. A geração original em inglês e a tradução de apresentação foram reutilizadas com proteção de orçamento, preservação do inglês/citações e fallback para falhas. Os 135 testes passaram; os 36 contextos predefinidos coincidiram com os registrados, e três consultas reais foram verificadas no navegador. A exportação do prompt histórico foi mantida para não quebrar pilotos antigos. Guias atuais foram atualizados, instruções históricas preservadas e limites de tradução/reprodução mantidos explícitos. Conferidos os 73 arquivos congelados e 77 anteriores, sem alteração das métricas. Ver docs/demo-v2-alignment.md.
