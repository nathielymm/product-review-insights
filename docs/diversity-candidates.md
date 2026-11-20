# Candidatos a três condições de variedade — 8 de novembro de 2026

## Conclusão da exploração

Os dados sustentam candidatos com diferentes graus de heterogeneidade de produtos e dispersão geral dos comentários. A combinação mais promissora para revisão é: cinco máscaras para cílios; cinco produtos diferentes de uma rotina capilar; cinco produtos de quatro áreas de cuidado pessoal. Não há IDs compartilhados entre esses três conjuntos.

A gradação compacto → intermediário → variado aparece na distância semântica média nas cinco amostragens, tanto na análise principal quanto em dois controles separados. Isso ainda não comprova três níveis de diversidade temática de oportunidades de melhoria: os agrupamentos semânticos dependem do número de grupos, e o padrão não é consistente em todos os indicadores. Não foram geradas respostas nem medidas de desempenho dos RAGs nesta exploração. Nenhum recorte está fechado.

## Candidatos prioritários

| Condição proposta | IDs de produto | Avaliações elegíveis disponíveis | Menor disponibilidade em um produto | Distância semântica média |
|---|---:|---:|---:|---:|
| Compacto: máscaras para cílios | 5 | 577 | 75 | 0,549 |
| Intermediário: rotina capilar | 5 | 1.438 | 109 | 0,646 |
| Variado: quatro áreas de cuidado | 5 | 1.921 | 95 | 0,800 |

As avaliações elegíveis passaram por deduplicação, limpeza de HTML, faixa de 20–200 palavras e detecção automática de inglês com score ≥0,90. O score do detector não é uma probabilidade calibrada e não substitui revisão manual. Essas contagens são menores que os totais do mapeamento anterior, que não aplicava esses filtros.

Em cada condição, a exploração usa 150 avaliações: 30 por produto, dando o mesmo peso aos cinco IDs. O tamanho do conjunto, o número de produtos, o idioma previsto e o limite de entrada do encoder foram mantidos iguais. Usamos cinco sementes de amostragem (11, 23, 37, 53 e 71). As sementes reutilizam avaliações do mesmo universo e não são cinco conjuntos independentes nem intervalos de confiança.

A distância é 1 − similaridade de cosseno entre embeddings MiniLM normalizados. Valores maiores indicam comentários mais dispersos nesse espaço. Não é nota de qualidade, porcentagem de diversidade, contagem de temas nem indicação de que um RAG é superior.

### Compacto: cinco máscaras para cílios

Mesmo tipo de produto e função principal, com diferenças de linhas, marcas e características como resistência à água e uso de fibras. Os cinco IDs são os do grupo compact_mascaras em configs/diversity-candidates.draft.json. Há três marcas preenchidas e distintas no atributo Brand, e dois IDs sem marca utilizável; a identidade de famílias continua provisória.

A inspeção inicial de dois comentários por produto encontrou relatos sobre aplicação, volume percebido, formação de grumos, duração e remoção. São exemplos para verificar coerência do escopo, não uma taxonomia de referência nem medidas de frequência. Relatos de desconforto devem ser tratados como experiências individuais, sem conclusões clínicas.

### Intermediário: cinco produtos de uma rotina capilar

- Shampoo: B0CDNZ7F2V.
- Condicionador leave-in: B01DD1NOZU.
- Máscara capilar: B0BV1FPZY6.
- Secador vendido com difusor: B01M1IEADO.
- Escova de cabelo: B00R1TAN7I.

Compartilham uma área de uso, mas têm cinco funções diferentes. Há cinco marcas distintas preenchidas no catálogo. Este candidato tem mais material elegível do que a alternativa intermediária de desodorantes, e evita repetir produtos do conjunto variado.

Na conferência do catálogo, B01M1IEADO e B00VIYHWUS são secadores com difusor, não difusores avulsos. Isso refina a leitura do mapeamento automático anterior. O candidato atual registra explicitamente a função secador; as regras automáticas por título continuam exploratórias.

### Variado: cinco funções em quatro áreas

- Shampoo: B012Q9NGE4.
- Cílios magnéticos com delineador: B08BZNW9NK.
- Conjunto de esmaltes: B01LBESKBO.
- Difusor avulso: B019GBG0IE.
- Escova dental a pilha: B000FEIOHW.

Representam cuidados capilares, maquiagem, unhas e higiene bucal. O maior contraste é entre as funções e áreas de uso dos produtos. Há quatro marcas distintas utilizáveis no atributo Brand e um ID com rótulo não informativo. Os exemplos inspecionados incluem problemas de aplicação, embalagem, encaixe, desempenho percebido e uso; sua relevância e os temas compartilhados precisam de anotação independente.

## Controles realizados

| Condição | Principal: 150 comentários | Faixas de tamanho iguais: 150 comentários | Proporções de notas iguais: 125 comentários |
|---|---:|---:|---:|
| Compacto: máscaras para cílios | 0,549 | 0,563 | 0,524 |
| Intermediário: rotina capilar | 0,646 | 0,653 | 0,637 |
| Variado: quatro áreas de cuidado | 0,800 | 0,809 | 0,792 |

No controle por tamanho, cada produto contribui com 20 textos de 20–39 palavras, oito de 40–79 e dois de 80–200. As faixas são iguais; o comprimento exato dentro de cada faixa ainda pode diferir.

No controle por notas, cada produto contribui com quatro notas 1–2 e 21 notas 4–5. Notas 3 foram excluídas apenas nessa verificação, pois pelo menos um produto do universo de candidatos não dispõe delas depois dos filtros. É uma análise de sensibilidade com 16% de notas baixas e 84% altas, não uma amostra representativa nem uma medida de sentimento. O controle por notas não iguala simultaneamente o tamanho dos textos, e o controle por tamanho não iguala simultaneamente as notas.

A ordem das três condições se manteve em 5/5 amostragens em cada uma dessas três versões. Isso mostra estabilidade frente a esses ajustes no universo examinado; não demonstra significância estatística populacional nem efeito causal puro da variedade.

## O que os indicadores ainda não demonstram

### A maior diferença está entre produtos

| Condição | Dispersão média dentro de um produto | Distância média entre os centros dos cinco produtos |
|---|---:|---:|
| Compacto: máscaras para cílios | 0,538 | 0,064 |
| Intermediário: rotina capilar | 0,547 | 0,298 |
| Variado: quatro áreas de cuidado | 0,564 | 0,687 |

As diferenças entre as condições são muito mais evidentes na distância entre produtos do que na variedade dentro de cada produto. É inadequado concluir, a partir disso, que cada produto do conjunto variado contém mais tipos de reclamação.

### Agrupamentos dependem da resolução

Treinamos partições semânticas compartilhadas em amostra com o mesmo número de comentários por produto. A tabela apresenta entropia normalizada dos grupos ocupados, uma aproximação exploratória de distribuição semântica, não cobertura temática de referência.

| Número de grupos | Compacto | Intermediário | Variado | Amostragens com ordem estrita compacto < intermediário < variado |
|---|---:|---:|---:|---:|
| 8 | 0,332 | 0,551 | 0,822 | 5/5 |
| 12 | 0,591 | 0,435 | 0,700 | 0/5 |
| 16 | 0,372 | 0,645 | 0,769 | 5/5 |

Com 12 grupos, o intermediário fica abaixo do compacto nesse indicador. Os rótulos de grupos não foram validados como temas de melhoria. Portanto, classificaremos as condições por características de produtos e dispersão de assunto; a diversidade temática precisa de inspeção e referência humana independente. O resultado do RAG não foi usado para selecionar candidatos.

## Outros candidatos examinados

Todos têm cinco IDs e a mesma amostra principal de 150 comentários:

| Candidato | Universo elegível | Menor universo por produto | Distância semântica média |
|---|---:|---:|---:|
| compact_brush_kits | 393 | 44 | 0,571 |
| compact_mascaras | 577 | 75 | 0,549 |
| intermediate_deodorants | 434 | 44 | 0,600 |
| intermediate_hair_routine | 2507 | 239 | 0,655 |
| varied_cross_category_a | 1916 | 95 | 0,790 |
| varied_cross_category_b | 590 | 72 | 0,734 |
| varied_disjoint | 1921 | 95 | 0,800 |
| intermediate_hair_disjoint | 1438 | 109 | 0,646 |

- compact_brush_kits: permanece na documentação, mas exige investigação. No ID B005V3AV5U, parte dos comentários descreve amostras/sombras de maquiagem em vez de um kit de pincéis. Uma busca lexical no universo elegível desse ID encontrou 27 textos com brush e 32 com sample/samples/eyeshadow/eye shadow, entre 100 comentários; os grupos podem se sobrepor. Isso é um sinal de possível inconsistência, não um classificador conclusivo nem motivo para excluir automaticamente comentários.
- intermediate_deodorants: alternativa de uma mesma função com apresentações e marcas diferentes. Tem 434 comentários elegíveis, mas um produto dispõe de apenas 44, limitando um corpus equilibrado maior. Um formato ainda não está confirmado pelo catálogo. Pode ser preferível se o interesse for variar formatos dentro de uma função, em vez de funções dentro de uma rotina.
- intermediate_hair_routine e os primeiros conjuntos mistos compartilham alguns produtos com outros candidatos. A tabela de sobreposição em docs/diversity-exploration-summary.json documenta isso. Não tratá-los como réplicas independentes.
- varied_disjoint e intermediate_hair_disjoint foram construídos para remover sobreposição de produtos, mantendo as funções descritas. Foram verificados novamente após a alteração. Não substituímos nem ocultamos os demais candidatos.

## Há volume suficiente?

Para a combinação prioritária, existem respectivamente 577, 1.438 e 1.921 comentários elegíveis. O produto com menor disponibilidade tem 75, 109 e 95 comentários, respectivamente. Isso sustenta a exploração com 30 por produto.

Considerando somente igualdade de quantidade por produto e sem controles adicionais, o limite comum seria 75 por produto, ou 375 por condição. Esse é um teto de disponibilidade antes da revisão de consistência e de idioma; não garante viabilidade de todas as estratificações de comprimento/notas nem riqueza temática suficiente. Não escolhemos o tamanho do experimento final nesta etapa.

O número de conjuntos também permanece uma decisão de desenho. Um conjunto por condição não permite separar completamente variedade, assunto, função e marca. Para alegar generalização sobre heterogeneidade, seria melhor ter mais de um conjunto independente em cada condição, com maior custo de referência e anotação. Três condições com um conjunto cada podem ser tratadas como estudos de caso comparativos, explicitando essa limitação.

## Próximos passos antes de fechar

1. Revisar consistência entre catálogo e comentários, famílias/variantes e o filtro de idioma. A inspeção feita aqui é pequena e exploratória.
2. Construir uma taxonomia de necessidades/problemas comuns e específicos, usando evidências independentes dos agrupamentos. Verificar se a gradação temática existe, além da diferença de assunto.
3. Decidir se o estudo comparará heterogeneidade de produtos/assuntos ou diversidade temática anotada. São conceitos relacionados, mas diferentes.
4. Escolher se haverá uma ou mais amostras independentes de produtos por condição, congelar critérios e definir o esforço de anotação.
5. Definir perguntas equivalentes no nível adequado. Perguntas específicas de cheiro, por exemplo, podem ser inaplicáveis a alguns conjuntos. Congelar critérios de aplicabilidade e abstenção antes de avaliar os RAGs.
6. Implementar e testar a restrição de escopo no runner e nos índices. O runner atual ainda não impõe scope_required. Não executar o rascunho final no índice global.

## Reprodução e rastreabilidade

```sh
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python -m pip install --no-deps --no-build-isolation -e .
.venv/bin/python scripts/explore_diversity.py
.venv/bin/python -m pytest -q
```

Também é possível instalar o extra analysis para obter o detector de idioma; o lock registra as versões efetivamente usadas. O script usa o encoder local em artifacts/pilot/encoder, com local_files_only=True. Nenhum comentário é enviado a serviço externo. HTML é removido após a deduplicação original, preservando a identidade auditada. O encoder recebe no máximo 200 tokens por comentário; 101 de 5144 comentários elegíveis codificados excederam esse limite. As proporções por conjunto estão no resumo técnico.

Fonte para a configuração determinística do detector: https://github.com/Mimino666/langdetect . Usamos langdetect 1.0.9 com seed 0; a detecção automática continua sujeita a erros.

A versão final da exploração cobre 28 IDs e 5.144 comentários elegíveis distintos. Arrays de embeddings, comentários, IDs de amostragem e logs permanecem em results/diversity-exploration, fora do Git. Apenas código, configurações e estatísticas agregadas são versionados. Os resultados antigos e índices de RAG foram preservados.

Passaram 22 testes, incluindo seleção determinística, detecção de falta de material, estratificação e distâncias em vetores conhecidos. Os hashes do arquivo de configuração, código, dependências, encoder, metadados e avaliações estão em docs/diversity-exploration-summary.json. Nenhuma medida de cobertura/fidelidade de respostas foi atribuída nesta exploração.
