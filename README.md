# Identificação de oportunidades de melhoria em produtos: comparação entre RAG tradicional e RAG enriquecido por análise temática

Projeto: `product-review-insights`.

#### Aluna:
#### Orientador(a):

---

Trabalho em desenvolvimento para a pós-graduação em [Inteligência Artificial Generativa e LLM da PUC-Rio](https://ica.ele.puc-rio.br/cursos/ia-generativa-large-language-models/).

- [Código](src/product_review_insights)
- [Progresso por entregas](docs/development-history.md)
- [Critérios e preparação da avaliação](docs/scoring-rubric.md)
- [Avaliação integrada e congelamento](docs/evaluation-freeze.md)
- [Geração principal concluída](docs/primary-generation.md)
- [Revisão humana parcial](docs/human-audit-completion.md)
- [Métricas principais e limites](docs/primary-evaluation-results.v1.md)
- [Análise de sensibilidade](docs/sensitivity-results.v1.md)
- [Discussão e conclusões integradas](docs/discussion-and-conclusions.v1.md)
- [Seleção no desenvolvimento](docs/development-parameter-selection.md)
- [Protocolo experimental](docs/protocol.md)
- [Reprodução local](docs/reproduction.md)
- [Auditoria dos dados](docs/data-audit.json)
- [Mapeamento exploratório de categorias](docs/category-map.md)
- [Candidatos a três condições de variedade](docs/diversity-candidates.md)
- [Revisão proposta de temas e consistência](docs/theme-consistency-review.md)
- [Recorte alinhado e corpora preparados](docs/study-preparation.md)

### Resumo

Este trabalho investiga a geração de insights sobre consumidores a partir de avaliações de produtos. Compara recuperação aumentada por geração (RAG) tradicional com recuperação enriquecida por agrupamento temático, utilizando o recorte All_Beauty do Amazon Reviews 2023 e o Gemma 3 4B executado localmente via Ollama. Foram avaliadas cobertura temática, fidelidade às evidências, critérios de propostas e controles, latência e volume de tokens. A avaliação principal reuniu 252 tentativas e a sensibilidade, 756. A seleção temática apresentou maior fidelidade média nos três casos principais, mas os ganhos não se mantiveram de forma estável entre tamanhos e sementes. Não houve vantagem consistente de cobertura. Os achados se limitam a uma referência parcial, anotação assistida por IA com revisão humana parcial das interpretações e execução local; não demonstram superioridade geral de um método.

### 1. Introdução

Avaliações de consumidores podem apoiar a identificação de elogios, reclamações e oportunidades de melhoria. A recuperação por similaridade pode concentrar o contexto em evidências redundantes. Investiga-se se uma seleção diversificada por temas aumenta a cobertura sem comprometer a fidelidade aos comentários.

O conjunto de dados utilizado é declarado como Amazon Reviews 2023, categoria All_Beauty, do McAuley Lab. O arquivo fornecido contém 701.528 registros e esquema compatível com avaliações. A correspondência exata com o arquivo oficial ainda exige verificação de procedência. O recorte de avaliações limita a generalização dos resultados e a inferência de participação de mercado.

O recorte alinhado contém três estudos de caso com cinco famílias cada: máscaras de cílios (547 avaliações), cuidados e ferramentas para cabelo (1.405) e funções de diferentes áreas (1.891). A análise principal utiliza as 3.843 avaliações elegíveis. A análise secundária usa 20, 40 e 60 avaliações por família, com três sementes. Desenvolvimento utiliza cinco famílias separadas, com 625 avaliações. Ver [recorte e preparação](docs/study-preparation.md).

As famílias operacionais não representam necessariamente versões idênticas. A revisão direcionada foi concluída: 20 comentários foram revisados pela usuária, cobrindo as 15 famílias; três registros exclusivamente sobre uso em animais foram excluídos e uma assinatura residual foi removida. Isso não constitui validação humana completa nem referência final. Ver [revisão dos dados](docs/final-corpus-qa.md) e configs/corpus-current.json. Um conjunto por condição permite estudos de caso e não isola causalmente o efeito da variedade.

### 2. Modelagem

O pipeline realiza leitura local de Parquet, exclusão de texto vazio e notas inválidas, remoção de duplicatas por produto e texto normalizado, redação heurística de emails, URLs e telefones e amostragem determinística por hash. Identificadores de usuários e imagens não são incorporados ao corpus derivado. A redação automática não garante anonimização completa; dados e respostas ficam fora do Git.

Quando duplicatas divergem em título, capitalização ou nota, usam-se representações canônicas determinísticas (mínimo lexicográfico de título/texto e menor nota). A nota não entra no prompt nem na busca; essa regra, preservada no congelamento, pode afetar sua distribuição descritiva.

As avaliações são segmentadas no limite do encoder MiniLM, convertidas em embeddings normalizados e indexadas em FAISS com similaridade de cosseno. MiniBatchKMeans agrupa os mesmos vetores; termos TF-IDF e exemplos representativos permitem inspecionar os agrupamentos. Os rótulos automáticos não constituem uma taxonomia validada.

O método tradicional seleciona os primeiros k resultados por similaridade. O temático seleciona primeiro um resultado por grupo dentro do mesmo conjunto de candidatos e completa as vagas por similaridade. Ambos utilizam o mesmo Gemma 3 4B, encoder, corpus, prompt, limite de contexto e parâmetros de geração. O enriquecimento atua na seleção das evidências, sem inserir resumos gerados adicionais.

A seleção operacional no desenvolvimento escolheu seis grupos e até oito trechos, com saída estruturada idêntica nos dois métodos. A configuração selecionada foi congelada tecnicamente em configs/evaluation-freeze.v1.json, junto às perguntas, fontes e regras de pontuação. A avaliação registrou erros de suporte e inferência, além de aspectos omitidos nas respostas. Cada comparação exige índice e corpus específicos do conjunto, verificados por hashes e identidades. As respostas devem citar evidências, atribuir observações às famílias corretas e se abster quando o contexto for insuficiente.

### 3. Resultados

A auditoria inicial encontrou 720 registros sem texto e 9.445 duplicatas segundo a regra adotada, resultando em 691.363 avaliações válidas e únicas. A amostra histórica de 10 mil registros pertence ao piloto global; os corpora do estudo somam 3.843 avaliações principais. A última suíte registrada teve 57 testes aprovados e uma integração real de recuperação no conjunto separado de desenvolvimento. Essas contagens descrevem a preparação dos dados, não a qualidade do RAG.

A geração principal congelada foi concluída: 252 tentativas nos três conjuntos, sem falhas de chamada. Doze saídas atingiram o limite de geração e ficaram com formato inválido; foram preservadas. As outras 240 passaram pela validação mecânica; a avaliação semântica posterior incluiu todas as tentativas. Foram preparados 102 itens de revisão após agrupar duplicatas exatas, mantendo as 252 tentativas e suas medições. Ver [registro da geração](docs/primary-generation.md).

As interpretações de uma amostra de 18 itens foram revisadas pela usuária, além de cinco itens de calibração, com auxílio do assistente. A anotação formal dos 102 itens únicos foi concluída pelo assistente, com 1.568 unidades de afirmação em contexto e cobertura das unidades de referência. Essa revisão parcial não constitui avaliação independente. As comparações usam as 252 tentativas, incluindo as 12 saídas cortadas; testes de software não são evidência de qualidade dos insights.

| Conjunto | Cobertura: tradicional / temático | Fidelidade: tradicional / temático | Mediana de tempo: tradicional / temático |
|---|---:|---:|---:|
| Máscaras | 13,7% / 6,7% | 79,0% / 84,7% | 7,21 s / 6,89 s |
| Capilar | 12,8% / 17,1% | 71,4% / 81,5% | 8,24 s / 9,66 s |
| Variado | 3,3% / 4,7% | 75,4% / 81,6% | 6,05 s / 7,98 s |

Cobertura é a média entre famílias elegíveis da referência parcial, nas nove perguntas factuais; fidelidade é a média de afirmações sustentadas nas 14 perguntas, após média das repetições. As anotações são assistidas por IA, com revisão humana parcial das interpretações. Ver [métricas, intervalos, propostas, controles e reprodução](docs/primary-evaluation-results.v1.md). A sensibilidade foi concluída em 27 cenários (756 tentativas), com 20/40/60 avaliações por família e três sementes. Cobertura e fidelidade variaram entre amostras, sem vantagem consistente do temático; sua mediana de tempo foi maior nos nove grupos. Ver [análise de sensibilidade, falhas e limites](docs/sensitivity-results.v1.md).

#### Discussão dos achados

A cobertura e a fidelidade medem propriedades distintas: uma resposta pode se apoiar corretamente em poucos relatos e ainda omitir aspectos relevantes. Na sensibilidade, a diferença média de cobertura favoreceu o temático em quatro dos nove grupos, o tradicional em quatro e empatou em um. A fidelidade favoreceu o temático em quatro e o tradicional em cinco. Em máscaras com 20 avaliações por família, a recuperação temática ganhou 9,88 pontos percentuais de cobertura, mas a resposta perdeu 0,46 ponto. A diversificação das passagens não garantiu sua incorporação na síntese.

Os denominadores elegíveis variam entre subconjuntos, com 58 combinações de pergunta/subconjunto sem apoio conhecido, cuja cobertura permanece indisponível. Assim, comparar tamanhos não isola o efeito do volume. A pertinência das propostas à tarefa atingiu 33,3% em ambos os métodos na sensibilidade, sob critério binário para a resposta inteira; isso indica dificuldade de atender integralmente à pergunta, sem significar ausência de qualquer sugestão útil. Hipóteses de melhoria podem ser formuladas sem dados de vendas, mas não se pode prever impacto comercial ou comprovar segurança a partir desses relatos.

O temático teve maior mediana de tempo nos nove grupos de sensibilidade. Foram mantidos uma falha de chamada, 42 formatos inválidos e 34 cortes, ocorrências que podem se sobrepor. Tempos e tokens descrevem esta execução; não foram medidos memória, CPU, energia ou custo monetário. A discussão completa, incluindo propostas, controles e limitações, está em [Discussão e conclusões](docs/discussion-and-conclusions.v1.md).

### 4. Conclusões

O trabalho implementou uma comparação reproduzível entre recuperação por similaridade e seleção de evidências diversificada por agrupamentos temáticos para investigar oportunidades de melhoria em produtos. Na configuração estudada, o enriquecimento temático não demonstrou ganho consistente de cobertura ou fidelidade. A maior fidelidade média dos casos principais não se manteve de forma estável na sensibilidade. Os resultados não estabelecem superioridade geral de uma arquitetura nem efeito causal da variedade.

A aplicação pode apoiar a organização de evidências e a formulação de hipóteses, mas sua utilidade para decisões de produto não foi validada com equipes ou resultados comerciais. As propostas precisam manter atribuição à família e ao relato, explicitar incertezas e ser revisadas. A referência é parcial e não independente; a pontuação foi feita pelo assistente, com revisão humana parcial de interpretações principais e sem revisão humana independente da sensibilidade. Perguntas dependentes, tamanhos aninhados, poucas repetições, versões de produtos e execução local limitam as inferências. A procedência exata do arquivo fornecido em relação à fonte oficial declarada também permanece a verificar.

Trabalhos futuros devem priorizar avaliação independente e ampliação da referência, investigar relevância para a pergunta e aproveitamento das evidências pelo gerador e validar hipóteses com especialistas e usuários finais. Novas estratégias devem ser avaliadas em outra versão experimental, preservando o congelamento e os resultados aqui documentados. O texto integrado está preparado para revisão acadêmica; os campos de identificação permanecem em branco.

---

Matrícula:

Pontifícia Universidade Católica do Rio de Janeiro

Pós-graduação em Inteligência Artificial Generativa e LLM
