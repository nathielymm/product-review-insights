# Identificação de oportunidades de melhoria em produtos: comparação entre RAG tradicional e RAG enriquecido por análise temática

Projeto: `product-review-insights`.

#### Aluna:
#### Orientador(a):

---

Trabalho em desenvolvimento para a pós-graduação em [Inteligência Artificial Generativa e LLM da PUC-Rio](https://ica.ele.puc-rio.br/cursos/ia-generativa-large-language-models/).

- [Código](src/product_review_insights)
- [Discussão e conclusões completas — análise por produto](docs/discussion-and-conclusions.v2.md)
- [Resultados e reprodução das métricas](docs/product-evaluation.v2-results.md)
- [Configuração e geração congeladas](docs/product-evaluation.v2-generation.md)
- [Inspeção separada das diferenças diagnósticas](docs/product-evaluation.v2-diagnostic-inspection.md)
- [Anotação e revisão humana parcial](docs/product-evaluation.v2-annotation-review.md)
- [Implementação e verificações técnicas](docs/product-evaluation.v2-implementation.md)
- [Interface demonstrativa local: como executar](docs/local-demo.md)
- [Auditoria dos dados](docs/data-audit.json)
- [Progresso por entregas e histórico preservado](docs/development-history.md)

### Resumo

Este trabalho investiga a identificação de oportunidades de melhoria em produtos a partir de avaliações de consumidores. Compara RAG tradicional com seleção de evidências enriquecida por agrupamentos temáticos internos a cada produto, usando o arquivo fornecido declarado como Amazon Reviews 2023 All_Beauty, embeddings MiniLM, FAISS e Gemma 3 4B local via Ollama. A avaliação compreendeu 36 respostas principais em três produtos, com referência parcial, anotação assistida e revisão humana das interpretações de 12 respostas. O temático apresentou maior cobertura média de conteúdo (18,75% contra 12,50%), enquanto o tradicional teve maior fidelidade média (85,33% contra 80,95%). Persistiram lacunas em qualificações, contrastes e propostas. Os resultados descrevem a configuração estudada, sem demonstrar superioridade geral, utilidade decisória validada ou impacto comercial.

### 1. Introdução

Avaliações de consumidores registram experiências sobre desempenho, aplicação, embalagem e expectativas de valor. Organizar esses relatos pode apoiar hipóteses de melhoria, mas exige preservar a atribuição ao produto, à pessoa e às condições descritas. Este estudo investiga se diversificar a seleção de evidências por agrupamentos temáticos amplia a cobertura sem comprometer a fidelidade, em comparação com a seleção pelo ranking de recuperação.

O arquivo Parquet fornecido é declarado como Amazon Reviews 2023, categoria All_Beauty, e contém 701.528 registros. A correspondência exata com o arquivo oficial ainda exige verificação de procedência. O recorte principal utiliza 1.209 avaliações de três produtos, analisados separadamente:

| Produto | Avaliações | Trechos indexados |
|---|---:|---:|
| Escova GranNaturals | 613 | 613 |
| Shampoo Pure Body Naturals Argan | 473 | 474 |
| Máscara de cílios Bold Lash | 123 | 123 |

O identificador operacional delimita o produto, sem excluir automaticamente mudanças de fórmula ou apresentação entre compras. Diferenças de versão e referências ambíguas a outros produtos precisam ser preservadas na interpretação. Os três casos foram escolhidos intencionalmente e não representam todos os consumidores ou produtos da categoria.

### 2. Modelagem

O processamento local realiza limpeza e deduplicação de avaliações, mantendo identidades de produto e fonte. Identificadores de usuários e imagens não entram no corpus derivado; dados, respostas, modelos e anotações individuais permanecem fora do Git. A redação heurística de informações pessoais não garante anonimização completa.

Os textos são segmentados conforme o limite do encoder MiniLM, convertidos em embeddings normalizados de 384 dimensões e indexados em FAISS. MiniBatchKMeans forma quatro agrupamentos exploratórios dentro de cada produto. Eles não constituem uma taxonomia temática independente validada.

Cada pergunta tem cinco buscas por aspectos em inglês. Seus resultados são combinados por Reciprocal Rank Fusion (RRF), formando um conjunto comum de até 80 candidatos, deduplicados por avaliação. O tradicional escolhe as primeiras oito avaliações desse ranking. O temático escolhe primeiro representantes dos agrupamentos disponíveis nesse mesmo conjunto e completa as vagas pelo ranking comum. Ambos usam o mesmo corpus, encoder, perguntas, gerador e orçamento de contexto. Nenhum método mistura produtos no contexto.

O Gemma 3 4B gera a resposta estruturada original em inglês, localmente via Ollama, com temperatura zero, semente 42, janela de 8.192 tokens e limite de 1.536 tokens de saída. O contexto tem limite de 12.000 caracteres serializados. A tradução para português ocorre apenas na apresentação e não altera a base da avaliação semântica ou as citações. As versões de código, entradas e parâmetros foram vinculadas por hashes no manifesto de congelamento.

A grade principal contém seis perguntas específicas por produto: quatro sobre aspectos de uso, uma de priorização de oportunidades e uma de controle sobre vendas. São 36 respostas principais, com uma geração por combinação de produto, pergunta e método. Há ainda 24 repetições diagnósticas de Q1/Q5, excluídas das métricas principais, e 36 traduções de apresentação. Não houve reparo, nova tentativa para selecionar melhor resposta ou descarte de falhas.

A referência parcial contém, por método, 55 alvos de conteúdo, 38 de qualificação e 16 de contraste. A cobertura usa as quatro primeiras perguntas; fidelidade, citações e propostas são avaliadas em Q1–Q5, e controles em Q6. As médias são calculadas dentro do produto e depois entre produtos com pesos iguais. Os métodos ficaram ocultos nas fichas de anotação; a usuária aprovou as interpretações de 12 respostas de uma amostra definida antes dos resultados. Isso não constitui avaliação independente ou revisão integral das afirmações.

### 3. Resultados

As 60 gerações em inglês e 36 traduções passaram no formato, sem erros de chamada ou cortes de tokens. Os agregados foram recalculados e coincidiram com a exportação. Essas verificações confirmam a execução e o cálculo, sem certificar os julgamentos semânticos ou a qualidade dos achados.

| Indicador médio | Tradicional | Temático |
|---|---:|---:|
| Conteúdo da referência disponível no contexto | 29,25% | 28,83% |
| Conteúdo reproduzido com apoio e citação | 12,50% | 18,75% |
| Qualificações reproduzidas com apoio e citação | 0,00% | 0,00% |
| Contrastes reproduzidos com apoio e citação | 8,33% | 8,33% |
| Fidelidade ao contexto | 85,33% | 80,95% |
| Suporte das próprias citações | 80,84% | 78,83% |
| Mediana de geração em inglês, com verificações | 5,92 s | 5,46 s |

Cobertura é relativa aos alvos completos da referência parcial, não a todos os temas do corpus. Fidelidade e citações são médias por resposta e produto, sem reunir afirmações como observações independentes. Não foi calculada nota global de qualidade.

| Produto | Cobertura: tradicional / temático | Fidelidade: tradicional / temático |
|---|---:|---:|
| Escova GranNaturals | 14,58% / 27,08% | 88,91% / 85,15% |
| Shampoo Pure Body Naturals | 10,42% / 10,42% | 91,26% / 80,93% |
| Máscara Bold Lash | 12,50% / 18,75% | 75,82% / 76,78% |

Ambos os métodos apresentaram de uma a duas oportunidades nas três perguntas Q5. Nos controles de vendas, ambos atenderam aos critérios de reconhecer insuficiência de evidência, distinguir hipóteses de previsões e indicar informação adicional nos três produtos. Nenhum controle satisfez simultaneamente os quatro critérios, devido a premissas factuais ou quantidades sem apoio adequado. Ver [critérios de propostas, controles, tokens, tempos e reprodução](docs/product-evaluation.v2-results.md).

#### Discussão dos achados

A seleção temática apresentou maior cobertura média de conteúdo da referência, com 18,75%, contra 12,50% do tradicional. Esse ganho ocorreu na escova e na máscara, com empate no shampoo. A fidelidade média ao contexto, porém, favoreceu o tradicional: 85,33%, contra 80,95%. O suporte pelas próprias citações também foi maior no tradicional, com 80,84%, contra 78,83%. Portanto, abordar mais aspectos não assegurou maior fidelidade, e nenhum método apresentou vantagem uniforme entre produtos e critérios.

A referência teve representação limitada nos contextos dos dois métodos: cobertura média de conteúdo de 29,25% no tradicional e 28,83% no temático. Além disso, parte das evidências disponíveis não foi reproduzida corretamente. Nenhum alvo completo de qualificação recebeu crédito nas respostas, e a cobertura de contrastes foi de 8,33% em ambos. Esses valores dizem respeito aos alvos específicos da referência parcial, com exigência de sentido completo e citação adequada; não demonstram ausência de qualquer condição, comparação ou achado útil.

Para identificar oportunidades de melhoria, é necessário preservar quem relatou a experiência, em qual produto e sob quais condições. Uma máscara recebida ressecada não equivale a uma unidade que secou rapidamente durante o uso; mudanças simultâneas de fórmula e aplicador não permitem atribuir isoladamente a piora a uma delas. Essas distinções mostram por que fluência, formato válido e quantidade de fontes não bastam para caracterizar profundidade analítica.

As propostas tiveram atendimento incompleto aos critérios. O vínculo com um problema apoiado e corretamente citado foi de 44,44% no tradicional e 37,78% no temático; a pertinência à pergunta alcançou 48,89% e 35,56%. Nenhum método explicitou satisfatoriamente uma qualidade valorizada a preservar. Listar elogios em outra parte da resposta não estabeleceu essa ligação. Embora ambos tenham apresentado de uma a duas oportunidades nas três perguntas de priorização, isso não comprovou justificativa de prioridade ou viabilidade das mudanças.

Todos os controles reconheceram que as avaliações não permitem prever qual melhoria aumentaria mais as vendas. Entretanto, nenhum passou simultaneamente nos quatro critérios, pois as respostas ainda continham premissas factuais ou quantidades sem apoio adequado. Assim, reconhecer um limite comercial não substitui o uso correto das fontes. A ausência de dados de vendas não impede formular hipóteses de melhoria, mas os relatos não demonstram frequência populacional, causa técnica ou impacto comercial.

As medianas locais de geração foram de 5,92 s no tradicional e 5,46 s no temático, incluindo as verificações do executor. Não houve erros de chamada ou cortes de tokens nas gerações, mas validade operacional não certifica qualidade semântica. Tradução, preparação e diagnósticos têm custos separados. Foram medidos apenas tempos de parede e tokens, sem CPU, memória, energia ou custo monetário. Ordem, carregamento e cache limitam a interpretação das diferenças de tempo.

As conclusões são limitadas a três produtos escolhidos intencionalmente, uma configuração local de modelo e agrupamentos exploratórios. A referência é parcial, e a anotação do assistente teve revisão humana das interpretações de 12 respostas, sem avaliação independente ou concordância entre avaliadores. A equivalência das traduções não foi integralmente certificada. A identidade operacional permite diferentes fórmulas e apresentações do mesmo produto, e há fontes com menções ambíguas a outras marcas. A procedência exata do Parquet em relação ao arquivo oficial declarado permanece a verificar. As seis saídas diagnósticas diferentes foram inspecionadas separadamente pelo assistente: houve alterações de achados, propostas e ressalvas, sem inclusão dessas repetições nas métricas principais. Essas limitações impedem generalizações populacionais ou conclusões causais.

A discussão ampliada, com os custos de tradução e os diagnósticos de estabilidade, está em [Discussão e conclusões completas](docs/discussion-and-conclusions.v2.md).

### 4. Conclusões

O trabalho implementou uma comparação reproduzível entre RAG tradicional e RAG enriquecido por seleção temática para identificar oportunidades de melhoria em produtos, com avaliações e temas organizados dentro de cada produto. A contribuição reúne recuperação local, geração com fontes rastreáveis e avaliação separada de cobertura, fidelidade, citações, propostas, controles e recursos de execução.

Na configuração estudada, o temático apresentou maior cobertura média de conteúdo, enquanto o tradicional apresentou maior fidelidade média e maior suporte das próprias citações. Os resultados variaram entre produtos e critérios, sem demonstrar superioridade geral de um método. As lacunas em qualificações, contrastes e preservação explícita de qualidades mostram que diversificar evidências, por si só, não assegura uma análise suficientemente contextualizada para orientar mudanças de produto.

O sistema pode apoiar a organização de experiências e a formulação de hipóteses, mas sua utilidade para decisões de produto ainda não foi validada com especialistas, usuários finais ou resultados comerciais. Uma sugestão apoiada em comentários continua sendo uma oportunidade a investigar, sem comprovar a causa de um problema, a eficácia de uma solução ou seu retorno comercial.

Como continuidade, devem ser priorizadas avaliação independente, ampliação da referência e verificação das ambiguidades de identidade nas fontes. Novos experimentos podem investigar recuperação mais alinhada aos aspectos das perguntas e geração que preserve condições, contrastes e vínculos entre achados e fontes. Mudanças devem formar uma nova versão experimental, preservando os resultados congelados. A inspeção separada das seis saídas diagnósticas diferentes foi concluída, sem alterar as métricas principais ou demonstrar estabilidade semântica geral. As conclusões se restringem aos dados, à referência parcial, à anotação assistida com revisão humana parcial e à execução local documentada.

---

Matrícula:

Pontifícia Universidade Católica do Rio de Janeiro

Pós-graduação em Inteligência Artificial Generativa e LLM
