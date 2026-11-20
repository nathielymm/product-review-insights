# Curly Co.: geração original em inglês e português apenas na apresentação

Estado: quatro gerações em inglês e quatro traduções de apresentação concluídas, sem cortes ou erros de formato. Todas as rodadas anteriores foram preservadas. A função original de geração foi restaurada diretamente; a revisão encontrou erros no inglês e erros adicionais na tradução, sem declarar ganho geral de fidelidade ou vencedor.

## O que foi restaurado

O executor chama diretamente product_review_insights.generation.generate, sem acrescentar instruções ao seu prompt. Foi usado o sistema STRUCTURED_SYSTEM original, o contrato original de groups/findings com citations, observation, proposal e uncertainty, e os parâmetros originais de geração: modelo/digest, temperatura 0, semente 42, janela de 8.192 tokens, teto de 1.536 tokens e 12.000 caracteres de contexto. A opção structured_output ficou ativa, como no experimento congelado.

As duas perguntas têm equivalentes explícitos em inglês para a geração. Foram retiradas as chamadas por avaliação e os campos/restrições de atribuição, suspeita e comprimento que se acumularam nos pilotos. Há uma chamada de geração por pergunta/método.

O corpus do Curly Co., os quatro agrupamentos internos do produto e a busca por aspectos foram mantidos. Os candidatos, trechos e ordem por pergunta/método coincidiram com a rodada 5. Isso restaura o gerador original, não reproduz o estudo inteiro com vários produtos ou sua antiga recuperação. A comparação permanece de desenvolvimento, no produto já explorado.

## Tradução separada e preservação das fontes

Depois de preservar o resultado inglês, uma chamada independente traduz apenas os textos não vazios de observação, proposta, incerteza e limites. O tradutor recebe chaves opacas e textos, sem o painel de fontes, grupos ou listas de citações. O código recoloca as traduções nos mesmos campos de uma cópia da estrutura, mantendo identificadores, ordem, número de achados e citações intactos.

O texto inglês e a estrutura original não são sobrescritos. O material das fontes vem diretamente das avaliações recuperadas e permanece em inglês. A validação rejeita chaves ausentes, referências em colchetes inseridas pelo tradutor e alterações de estrutura. Essas barreiras não demonstram que a tradução preservou o sentido; houve conferência qualitativa separada.

A apresentação tem teto próprio de 1.536 tokens, registrado separadamente. Seu custo não deve ser ocultado como se fosse geração gratuita. Não houve reparo, revisão automática de fatos, tradução pós-falha repetida ou escolha da melhor saída. Inglês e português brutos, contratos e tempos ficam preservados.

## Resultados operacionais

| Pergunta | Método | Achados em inglês | Avaliações citadas | Geração em inglês | Tradução de apresentação |
|---|---|---:|---:|---:|---:|
| P01 | Tradicional | 1 | 8 | 3.19 s | 2.31 s |
| P01 | Temático | 3 | 8 | 4.51 s | 3.04 s |
| P02 | Tradicional | 2 | 8 | 4.15 s | 3.70 s |
| P02 | Temático | 4 | 8 | 7.61 s | 8.35 s |

Foram fornecidas oito avaliações por resposta. Todas foram citadas em cada saída inglesa, mas uma lista com oito referências não comprova que cada uma sustenta todas as frases. Os achados originais podem conter várias afirmações e fontes; sua quantidade não é comparável diretamente aos oito achados unitários das rodadas 4/5.

A geração usou 5.945 tokens de entrada e 1.351 de saída no total. A apresentação acrescentou 1.667 de entrada e 1.377 de saída. A rodada 5 usara 32 chamadas e 24.395/3.101 tokens de entrada/saída. Não é uma comparação isolada de idioma: mudaram contrato, número de chamadas, granularidade e parâmetros de apresentação. Tempos são de uma execução em ordem fixa, sem controle de carga compartilhada, não latência típica. Não houve monitoramento de memória, CPU, processos ou energia.

## Conferência do inglês contra as fontes

Na primeira pergunta, o tradicional produziu uma síntese única e ampla sobre colapso. Ela reúne as oito referências e enfatiza condições que não são estabelecidas como mais propensas ao problema. O uso de cabelo grosso, por exemplo, aparece no contexto, mas isso não demonstra que seja uma condição especialmente associada ao colapso. A resposta perdeu detalhes e divergências disponíveis nas avaliações.

O temático separou três achados, abordando chegada do produto, colapso/fixação e benefícios de desempenho. Ainda agrupou experiências distintas e apresentou uma limitação geral de ausência de informações sobre produtos anteriores, embora o contexto inclua comparação com outros difusores. Os casos de dobrado/desdobrado não reapareceram da mesma forma, mas o fato foi pouco explorado; sua omissão não demonstra que a dificuldade tenha sido resolvida.

Na segunda pergunta, ambos propuseram investigar durabilidade/fixação. O tradicional transformou a impressão de que peças pareciam coladas em uma observação mais afirmativa. O temático preservou prazos de duas e cinco meses, mas atribuiu a uma avaliação o movimento de mexer o difusor descrito em outra fonte. Também falou de conexão cabeça-corpo do secador em uma proposta, confundindo componentes. Algumas propostas recorrem a problemas descritos em outras partes da resposta, sem o vínculo local claro com as referências do respectivo achado.

Esses erros já estavam no inglês. Não devem ser atribuídos à tradução, e restaurar a configuração não comprova automaticamente que ela seja mais fiel para estas perguntas e evidências. Não houve referência exaustiva, anotação independente ou taxa numérica de fidelidade/profundidade.

## Conferência da tradução separadamente

As quatro traduções passaram nas barreiras de estrutura e preservação de citações, mas algumas palavras alteraram ou prejudicaram o sentido. Na primeira resposta tradicional, “collapse” apareceu como “desabafo” em parte do texto; na primeira temática, “scalp” virou “calva”. Houve ainda estrangeirismos e construções como “curl” e concordância inadequada. Esses são problemas da apresentação, distintos dos erros já presentes na geração inglesa.

A tradução também preservou erros do inglês, como a atribuição de movimento à avaliação errada. Isso confirma a necessidade de consultar o original para localizar a etapa da falha. O tradutor não recebeu instrução para revisar fatos e não foi usado para melhorar silenciosamente a geração.

A conferência foi feita pelo assistente com os métodos visíveis. Ela não certifica tradução humana independente, qualidade linguística integral ou ausência de outros erros. As traduções brutas não foram substituídas por uma versão manual para favorecer o resultado.

## Leitura da comparação e decisão

Foi implementada a separação desejada: análise em inglês pelo gerador original, tradução apenas depois e fontes originais preservadas. O modelo permaneceu o mesmo. O piloto passou de 32 chamadas de geração para quatro de geração e quatro de tradução.

A configuração original voltou a produzir sínteses com vários relatos, em vez de oito blocos analisados separadamente. Isso simplificou a execução, mas a leitura ainda encontrou generalizações, mistura de detalhes e perda de modalidade. O temático produziu mais achados nesta execução; isso não estabelece maior profundidade ou melhor fidelidade. Não há vencedor demonstrado.

A restauração fica registrada como controle de desenvolvimento. Ela não é promoção automática à interface ou à avaliação final. Erros de geração e de tradução foram documentados separadamente, sem alterar as respostas anteriores. Qualquer etapa futura deve usar novos destinos e preservar os originais, inclusive quando um ajuste não melhora a qualidade.

## Preservação, testes e reprodução

Os 65 arquivos anteriores registrados antes da execução foram verificados por hash. O código original de geração não foi editado. Os artefatos congelados e as cinco rodadas anteriores permanecem intactos. As respostas inglesas continuam idênticas às salvas antes da tradução.

Passaram 90 testes antes da geração e 91 na conferência final. Incluem preservação do original, fontes excluídas do pedido de tradução, IDs e estrutura mantidos, rejeição de chaves inválidas e recusa de sobrescrita. Não são certificação semântica ou linguística. Os agregados foram reproduzidos com igualdade byte a byte, sem novas chamadas.

Configuração: configs/curly-product-pilot.v6-original-english.json. Executor: scripts/run_product_original_pilot.py. Resultados privados: results/product-pilot/curly-v6-original-english/. A interface continua usando sua configuração anterior até eventual decisão explícita de integrar este fluxo.

```sh
.venv/bin/python scripts/report_product_original_pilot.py --output results/product-pilot/curly-v6-original-english/novos-agregados.json
```

O executor e o exportador recusam destinos existentes. Dados, respostas individuais, fontes, prompts completos e revisão semântica ficam fora do Git. Os relatórios públicos trazem somente agregados e discussão.
