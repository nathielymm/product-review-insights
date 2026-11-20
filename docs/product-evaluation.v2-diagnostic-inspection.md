# Inspeção separada das diferenças diagnósticas — v2

A inspeção das seis saídas diagnósticas diferentes foi concluída pelo assistente, após aprovação da discussão e das conclusões pela usuária. Não houve nova chamada ao modelo, troca de resposta principal, revisão dos rótulos principais ou recálculo para escolher uma repetição melhor. Os resultados numéricos congelados permanecem iguais.

## Procedimento

Foram comparadas as 24 repetições de Q1/Q5 com suas respectivas respostas principais: 18 eram textualmente idênticas e seis diferiam. Em cada uma das seis diferenças, foram conferidos inglês original, campos alterados, achados restantes, citações e trechos efetivamente enviados ao modelo. Contexto, ordem das fontes e requisição completa ao modelo coincidiram com os do principal nos seis pares.

As seis saídas correspondem a três comparações distintas de texto e contexto, cada uma observada duas vezes. A igualdade dos textos completos foi conferida, e cada tentativa continua registrada separadamente. A inspeção é qualitativa e orientada às mudanças; não é uma nova anotação exaustiva de afirmações nem uma segunda avaliação independente. Não foram produzidas taxas de fidelidade das repetições ou uma nota de estabilidade semântica.

## O que mudou

| Padrão observado | Saídas | Interpretação da inspeção |
|---|---:|---|
| Alteração de achados e propostas | 2 | Algumas formulações anteriores inadequadas foram removidas e detalhes apoiados foram acrescentados. Ao mesmo tempo, surgiram problemas de atribuição, generalização e citação. As propostas também mudaram, mantendo caráter de hipótese. |
| Paráfrase local e atribuição mais firme nos limites | 2 | A mudança de redação sobre volume preservou o achado, mas a ressalva final passou a atribuir as queixas a características individuais e técnicas de uso sem apoio suficiente. Problemas anteriores de pessoa e parte corporal persistiram. |
| Mudança nas ressalvas e no foco de investigação | 2 | Observações e propostas ficaram iguais ao principal. Mudou o foco de investigação, de orientação de uso para adequação da formulação, mantendo a incerteza. Os erros factuais anteriores não foram corrigidos. |

Na primeira categoria, a inspeção encontrou tanto melhorias locais quanto problemas novos; por isso, não cabe classificar a repetição inteira como superior. A retirada de uma formulação incorreta não impede que outra afirmação troque a pessoa da experiência ou cite uma fonte inadequada. Variantes de desenho de cerdas continuaram sendo propostas a investigar, sem confirmação de causa ou eficácia.

Na segunda categoria, a diferença não se restringiu ao estilo. Uma paráfrase de perda de volume foi acompanhada de mudança no grau de atribuição a condições e técnicas. As fontes descrevem algumas condições individuais, mas não demonstram que a técnica explique as queixas. Essa distinção foi registrada sem alterar o julgamento da resposta principal.

Na terceira categoria, a reformulação preservou o reconhecimento de limites e não acrescentou uma observação nova. A nova redação não eliminou os problemas já presentes nos achados inalterados. Portanto, diferença textual não equivale automaticamente a novo erro, correção ou ganho de profundidade.

## Alcance e preservação

A identidade com o principal permaneceu em 7/12 repetições no tradicional e 11/12 no temático. Esses números descrevem esta grade e não estabelecem robustez geral, qualidade superior ou uma causa para a variação. Foram observadas diferenças apesar de as requisições registradas serem iguais; os registros não permitem identificar o mecanismo responsável.

As métricas principais continuam baseadas nas mesmas 36 respostas, com denominadores, anotações e agregados intactos. Os diagnósticos não foram incluídos como casos independentes e nenhuma resposta melhor foi selecionada para substituir a principal. As 12 interpretações humanas aprovadas continuam sendo a revisão parcial principal; esta inspeção adicional foi feita pelo assistente, sem ampliar a carga de revisão da usuária.

A referência parcial, a anotação assistida e os três produtos intencionalmente selecionados continuam limitando as conclusões. A inspeção encerra a pendência de leitura das seis saídas, sem demonstrar estabilidade semântica geral ou validar soluções de produto. Textos, fontes, posições e justificativas individuais permanecem no armazenamento local ignorado pelo Git. O repositório contém este relato e o [manifesto agregado](product-evaluation.v2-diagnostic-inspection.json).

Foram conferidos os hashes das gerações e traduções, das anotações finais, dos casos e agregados principais, dos 73 arquivos congelados e dos 77 arquivos anteriores registrados. O [relatório de métricas](product-evaluation.v2-results.md) foi preservado como publicado; suas menções à inspeção então pendente correspondem ao estado anterior a este complemento. A atualização documental não recalcula nem substitui seus resultados.
