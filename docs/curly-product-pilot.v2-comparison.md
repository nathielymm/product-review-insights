# Curly Co.: segunda rodada com aspectos e achados menores

Estado: quatro novas tentativas concluídas e preservadas, comparadas às quatro da primeira rodada. É desenvolvimento no mesmo produto já inspecionado, não avaliação final independente. A busca mudou de forma verificável; a geração ainda não atingiu o contrato proposto. Não há vencedor ou taxa de profundidade/fidelidade calculada.

## O que mudou e o que foi mantido

Foram mantidos o corpus de 804 avaliações/805 trechos, os quatro agrupamentos locais, os vetores, o modelo/digest, a versão do Ollama, as duas perguntas em português, a seleção de até oito trechos, 12.000 caracteres de contexto, janela de 8.192 tokens, limite de 1.536 tokens de saída e temperatura 0/semente 42. O índice foi lido, sem nova preparação ou reagrupamento. Todos os artefatos anteriores registrados antes da execução foram conferidos por hash depois dela.

A busca passou a usar cinco consultas explícitas em inglês, correspondentes a encaixe/fixação, colapso no uso, durabilidade/integridade, secagem/cachos/frizz e portabilidade/armazenamento. São aspectos da tarefa definidos antes das novas respostas, não categorias verdadeiras exaustivas do corpus. Os dois métodos usam os mesmos aspectos; cada consulta traz até 16 candidatos. A união é ordenada por Reciprocal Rank Fusion (mesmo peso, constante 60), limitada a 80 candidatos, mantendo um trecho por avaliação. Não há mínimo garantido por aspecto no contexto final, nem teste estatístico de relevância.

O tradicional escolhe os primeiros resultados dessa ordenação compartilhada. O temático seleciona inicialmente grupos distintos entre esses mesmos candidatos e completa por ranking. Os hashes dos candidatos foram iguais para ambos os métodos em cada pergunta. Os aspectos orientam a busca; os agrupamentos vetoriais locais continuam sendo o mecanismo de diversificação temática. Um aspecto não equivale a um cluster.

A geração passou a permitir até seis achados curtos, cada um com um único aspecto, avaliação citada, trecho literal, observação, condição explicitamente relatada ou campo vazio, hipótese de melhoria e verificação. Há limites de caracteres e rejeição de citações não literais. Na primeira pergunta, o campo de proposta deve ficar vazio. Qualidades valorizadas são separadas dos problemas. Classificação, fidelidade e idioma continuam exigindo revisão: não são comprovados pelo esquema.

Busca por aspectos, deduplicação por avaliação e contrato de geração mudaram juntos. A comparação entre rodadas não identifica causalmente qual componente provocou cada diferença. Não houve nova tentativa para substituir saída rejeitada ou escolha da melhor resposta.

## Recuperação: comparação medida

Cada célula mostra grupos vetoriais representados no conjunto indicado; isso não mede cobertura semântica da resposta.

| Pergunta | Rodada | Candidatos únicos | Grupos nos candidatos | Grupos no contexto tradicional | Grupos no contexto temático | Trechos comuns entre métodos |
|---|---|---:|---:|---:|---:|---:|
| P01: problemas e condições | 1 | 80 | 2 | 2 | 2 | 8 de 8 |
| P01: problemas e condições | 2 | 72 | 4 | 2 | 4 | 6 de 8 |
| P02: melhorias e qualidades | 1 | 80 | 2 | 1 | 2 | 7 de 8 |
| P02: melhorias e qualidades | 2 | 69 | 2 | 2 | 2 | 8 de 8 |

Na P01, os dois grupos antes ausentes entraram no conjunto de candidatos e foram selecionados pelo temático. As novas fontes incluem condições concretas, como contato com o couro cabeludo, uso em viagem e formato da superfície do difusor. Isso amplia o material disponível para investigar, sem provar que todas as condições foram interpretadas corretamente. A concentração nos grupos 0 e 1 continua: apenas um candidato de cada um dos outros dois grupos entrou na P01.

Na P02, os candidatos continuaram restritos a dois grupos. A busca por aspectos não garante representar todos os clusters nem deveria forçar trechos irrelevantes a fazê-lo. Ambos os métodos receberam exatamente as mesmas oito fontes, em ordem diferente, nessa pergunta.

## Geração: o que foi observado

As quatro novas saídas eram JSON parseável e não tiveram falha de chamada ou corte, mas todas foram rejeitadas pelo novo contrato por pelo menos uma citação textual não literal. Foram preservadas como saídas rejeitadas, sem correção de texto, tradução ou reconstrução de uma resposta aceita. A primeira rodada não exigia esse campo; por isso não é correto interpretar sua aceitação estrutural como superioridade semântica sobre a segunda.

| Pergunta | Método | Achados declarados | Avaliações referenciadas* | Trechos literais / declarados* | Idioma das observações, conferido pelo assistente | Tempo |
|---|---|---:|---:|---:|---|---:|
| P01 | Tradicional | 6 | 6 | 5/6 | Inglês | 7,72 s |
| P01 | Temático | 6 | 5 | 5/6 | Inglês | 8,51 s |
| P02 | Tradicional | 6 | 5 | 5/6 | Português | 8,71 s |
| P02 | Temático | 6 | 6 | 4/6 | Português | 35,03 s |

*Contagens diagnósticas extraídas do JSON rejeitado, não achados aceitos, pontuação de fidelidade ou comprovação do apoio das interpretações. São 19 trechos literalmente presentes no conjunto de 24 campos declarados. Uma frase pode ser copiada corretamente e interpretada de forma incorreta. Houve tanto combinação de passagens não contíguas quanto reformulação de palavras/ordem e correção de um erro de grafia da fonte; a rejeição literal não tem sempre a mesma gravidade semântica.

Limitar a seis achados de uma fonte cada também limita mecanicamente a seis avaliações citáveis por resposta, contra oito na primeira rodada. A queda de quantidade de referências não demonstra pior recuperação ou pior fidelidade. Em duas respostas, uma avaliação foi usada para mais de um achado; avaliação única e número de achados são contagens distintas.

Tempos são de uma chamada por combinação, em ordem fixa e sem controle da carga compartilhada. A chamada de 35,03 s não autoriza inferir custo estável ou atribuir a demora ao método. Tokens são registrados separadamente; não foram medidos CPU, memória, energia ou custo monetário.

## Leitura qualitativa contra a primeira rodada

### P01: problemas, condições e experiências divergentes

Antes, havia três achados longos em cada método, e o tradicional misturava experiências com prazos diferentes. Agora os campos observacionais ficaram menores, mas isso não garante melhor interpretação. No tradicional, uma condição de viagem foi atribuída a uma fonte que apenas mencionava viagem futura; houve ainda combinação de frases não contíguas no campo de citação. No temático, o formato plano da superfície foi interpretado como resultado “plano” no cabelo, alterando o sentido do relato. Além disso, ambos desobedeceram ao idioma português solicitado nessa pergunta.

Portanto, o ganho de material disponível na recuperação não se converteu em qualidade de resposta demonstrada. Há mais separação estrutural e condições concretas nas fontes, mas ainda erros de sentido, atribuição e uso dos campos.

### P02: melhorias, qualidades e validação

Na primeira rodada, o tradicional sugeriu investigar material/fixação, mas acrescentou causalidade sem apoio; o temático resumiu elogios e não propôs melhorias apesar das reclamações disponíveis.

Nesta rodada, ambos incluíram hipóteses de melhoria. O tradicional propôs investigar estabilidade; o temático abordou fixação e materiais. Essa é uma diferença observada em relação à omissão anterior, não validação das soluções. Persistiram problemas: um encaixe elogiado foi classificado como problema em ambos, e definição/volume dos cachos receberam interpretação mais específica do que a respectiva fonte sustenta. A proposta temática sobre colagem não está demonstrada na própria fonte individual que acompanha esse achado; no máximo é uma hipótese, sem diagnóstico estabelecido.

Os dois métodos receberam as mesmas oito fontes nessa pergunta. Não se pode atribuir uma eventual vantagem ao acesso a mais evidências. O formato novo melhorou a possibilidade de inspeção dos achados, mas a coerência entre observação, classificação, condição e proposta permanece insuficiente.

## Decisão de desenvolvimento

A segunda rodada implementou as duas mudanças e expôs um limite adicional: exigir que o modelo copie citações literalmente e preencha diversos campos não assegurou qualidade, e introduziu quatro rejeições do contrato. O piloto não será promovido à configuração final nem usado para declarar superioridade de um RAG.

A próxima hipótese de desenvolvimento é simplificar a geração e retirar do modelo a tarefa de reproduzir a fonte: manter um identificador validado e apresentar o trecho original diretamente pelo sistema. Isso não dispensaria revisão do apoio semântico. Também é necessário assegurar português, tratar propostas como hipóteses e verificar condições de uso sem inferência. Antes de novas gerações, convém testar essas exigências de forma pequena e separada; elas não foram corrigidas silenciosamente nesta rodada.

## Rastreabilidade e reprodução

Configuração: configs/curly-product-pilot.v2-aspects.json. Executor: scripts/run_product_aspect_pilot.py. Dados, candidatos, prompts completos, respostas brutas, rejeições e revisão individual ficam em results/product-pilot/curly-v2-aspects/, ignorado pelo Git. A conferência foi do assistente, com métodos visíveis, sem referência exaustiva ou avaliação humana independente.

A suíte passou com 72 testes antes da geração e 73 na conferência final, incluindo união por aspectos, deduplicação, citação ligada à própria fonte, limites dos campos e preservação dos resultados. Esses testes não comprovam fidelidade ou profundidade. Os agregados públicos não contêm textos individuais.

```sh
.venv/bin/python scripts/report_product_aspect_pilot.py --output results/product-pilot/curly-v2-aspects/novos-agregados.json
```

O exportador exige as quatro tentativas de cada rodada e recusa sobrescrita. A execução de novas gerações também recusa resultado existente; para repetir, usar outra configuração/destino, sem apagar esta rodada. A exportação é determinística para os arquivos existentes; a geração não tem igualdade textual garantida.
