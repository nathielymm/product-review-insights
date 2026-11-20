> Histórico: a proposta de 750 avaliações foi substituída pelo desenho de corpus elegível completo descrito em recorte-e-corpora.md e docs/study-preparation.md.

# Proposta concreta de recorte final

Status: pronta para alinhamento com a usuária; ainda não registrada como aprovada nem como corpus congelado.

## Pergunta central e desenho

Comparar RAG tradicional e RAG enriquecido por agrupamento temático na identificação de oportunidades de melhoria fundamentadas em avaliações de consumidores. Examinar três estudos de caso com heterogeneidade funcional diferente, mantendo iguais o número de grupos de produto e o volume de comentários por grupo.

Os rótulos compacto, intermediário e variado descrevem as funções/áreas dos produtos e a dispersão geral observada na exploração. Não representam três níveis comprovados de quantidade de temas. Com um conjunto por condição, os resultados serão de estudos de caso; não isolam um efeito causal puro da variedade nem representam todo o mercado.

## Composição proposta

| Condição | Composição | Famílias operacionais | Comentários por família | Total planejado |
|---|---|---:|---:|---:|
| Compacta | Máscaras para cílios, com a mesma função principal | 5 | 50 | 250 |
| Intermediária | Shampoo, condicionador/leave-in, máscara capilar, secador com difusor e escova de cabelo | 5 | 50 | 250 |
| Variada | Shampoo, cílios magnéticos com delineador, esmaltes, difusor e escova dental a pilha | 5 | 50 | 250 |
| Total | Três conjuntos sem parent_asin compartilhado | 15 | 50 | 750 |

Os IDs estão em configs/study-scope.proposed.json. O conjunto intermediário usa produtos diferentes dos presentes no variado, mesmo quando há funções relacionadas. Nenhuma resposta final dos RAGs foi usada para essa seleção.

### Unidade: grupo funcional representado por parent_asin

Usar o grupo parent_asin como família operacional, preservando os ASINs dos itens e o contexto histórico. Isso não equivale a identificar uma única fórmula, um SKU exato ou fabricantes independentes. Os rótulos devem ser neutros quando a versão não estiver confirmada.

Essa escolha acomoda os três grupos em que a auditoria encontrou múltiplos ASINs de item. A análise só atribuirá características a uma versão quando houver evidência correspondente. Uma expectativa de waterproof, por exemplo, pode ser descrita quando o próprio comentário a declara; o título representativo do catálogo não deve ser aplicado automaticamente a todas as versões históricas.

Estudar versões exatas seria outro desenho: exigiria metadados históricos adicionais e nova checagem de volume. Não é necessário para comparar a geração de insights no nível funcional, desde que a limitação seja explícita.

## Volume e seleção

A exploração anterior utilizou 30 comentários por grupo. Proponho aumentar o corpus principal para 50, mantendo a contribuição igual de cada família. O número é uma decisão pragmática de disponibilidade e esforço de referência/anotação, não um cálculo de poder estatístico nem garantia de saturação temática.

Reservar os 90 comentários da auditoria inicial para desenvolvimento do codebook e discussão. Eles não entram no corpus principal proposto. Isso separa os exemplos já discutidos da futura amostra de avaliação; não significa que toda a exploração prévia dos dados seja independente do desenho.

Após essa reserva, continuam disponíveis:

| Conjunto | Comentários elegíveis restantes | Menor disponibilidade em uma família | Quota proposta por família |
|---|---:|---:|---:|
| Compacto | 547 | 69 | 50 |
| Intermediário | 1.408 | 103 | 50 |
| Variado | 1.891 | 89 | 50 |

Os 750 comentários são um alvo de preparação, não um corpus já exportado e aprovado. A amostra será determinada por hash com seed 20261108, sem escolher os comentários por tema, nota ou desempenho do RAG. Manter os demais como reserva na mesma ordem determinística. Se a revisão de qualidade inviabilizar uma quota, registrar a razão e revisar a configuração explicitamente; não trocar famílias silenciosamente.

As medidas de dispersão anteriores descrevem as amostras de exploração, não antecipam as medidas do novo corpus. Descrever o corpus preparado sem mudar a seleção para forçar uma ordem dos indicadores.

## Inclusão, exclusão e tratamento

- Fonte: o Parquet All_Beauty fornecido e os metadados oficiais já obtidos, com hashes registrados.
- Texto em inglês detectado automaticamente com langdetect 1.0.9, seed 0 e score ≥0,90, sujeito a conferência. O score não é probabilidade calibrada.
- De 20 a 200 palavras após limpeza de HTML. Sem tradução no experimento principal.
- Texto não vazio e nota válida de 1 a 5. Usar a mesma identidade de deduplicação da exploração, documentando a escolha da menor nota quando duplicatas conflitam; isso não preserva necessariamente a distribuição bruta original.
- Sem balanceamento artificial de elogios/reclamações ou seleção por assuntos. Registrar as distribuições de notas e tamanhos resultantes.
- Sem corte temporal adicional nesta proposta. Preservar timestamps e descrever a cobertura histórica; não inferir situação atual do produto ou mercado.
- Comentários genéricos, diferenças de versão, divulgação de gratuidade e alegações de incentivo não são excluídos automaticamente. Aplicar marcadores e limitar a interpretação.
- Uma descrição explicitamente de outra classe de produto precisa ser revisada antes da exclusão, com motivo documentado. Comparar marcas ou preferir outra opção não basta para declarar inconsistência.
- Separar produto, embalagem/proteção, anúncio/oferta, entrega e atendimento ao inferir melhorias.
- Manter relatos de desconforto e opiniões de saúde como relatos atribuídos, sem concluir eficácia clínica, causalidade ou segurança.
- Não incorporar user_id ou imagens. Aplicar redação e conferir dados pessoais residuais antes do congelamento; dados brutos, textos, modelos e respostas continuam fora do Git.

## Desenvolvimento e avaliação

Usar prospectivamente cinco famílias diferentes para ajustes adicionais de prompt, agrupamento e parâmetros: B07G19ZXWB, B00NQ2CCOQ, B09P3ZMV55, B086H4C8QB e B09XBSDCXP. Foi verificado que não se sobrepõem às 15 famílias de avaliação e que cada uma tem pelo menos 50 comentários nos pools atuais. O piloto global anterior permanece como exploração histórica; não será apresentado como teste final independente.

Construir corpus/índice separado por conjunto. Os dois métodos devem consultar exatamente o mesmo corpus e ter os mesmos limites de contexto, encoder, modelo e geração. O enriquecimento temático altera a seleção das evidências. Definir parâmetros usando desenvolvimento e congelá-los antes de gerar respostas finais. O índice global e o runner atual ainda não garantem a restrição desse recorte: essa checagem faz parte da implementação seguinte.

As 16 perguntas continuam como rascunho. Adaptar a referência e a aplicabilidade ao nível de conjunto/família, mantendo perguntas comparáveis e abstenção quando faltarem evidências. Não exigir que todos apresentem o mesmo problema específico, nem tratar ausência de pedido explícito como motivo para inventar uma solicitação.

Se todas as 16 perguntas forem mantidas, três conjuntos × dois métodos × três repetições resultarão em 288 respostas. Isso é planejamento, não resultado produzido. As repetições não são réplicas independentes de variedade. A avaliação de limites fica separada da cobertura temática; a qualidade das propostas inferidas deve ser distinguida da sustentação de afirmações factuais.

Construir a referência com evidências do corpus definitivo e independentemente dos clusters do método temático. A aprovação de cinco interpretações pela usuária é um alinhamento inicial, não validação dos 90 comentários nem referência final pronta. Não é necessário concluir a revisão dos 90 para decidir o recorte estrutural; a validação da referência de avaliação é uma etapa distinta.

## O que esta decisão fixa e o que continua como preparação

Após o alinhamento, ficam definidos: as três condições e suas famílias, a unidade funcional, as quotas de 50 por família, as regras de elegibilidade e a separação da auditoria/desenvolvimento. Essas decisões devem ser registradas antes de olhar resultados finais dos RAGs.

Continuam pendentes a execução da preparação com preservação da linhagem dos itens, QA do texto/idioma/identidade, hashes dos corpora, verificação de escopo na recuperação, fechamento do benchmark e parâmetros e construção/anotação da referência. Essas pendências não mudam a escolha estrutural sem uma alteração de versão explícita.

O trabalho termina com a comparação real de cobertura temática, fidelidade às evidências, latência e recursos computacionais nos três estudos de caso. Um resultado sem superioridade do método temático é válido. O repositório GitHub privado e o primeiro envio continuam sujeitos à revisão já combinada.
