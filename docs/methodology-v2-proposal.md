# Proposta v2: análise aprofundada de um produto por consulta

Estado: proposta para alinhamento, sem ativação de nova configuração, alteração da v1 ou geração de novas respostas de avaliação. A seleção por produto já disponível na interface demonstra o recorte; não equivale à implementação ou avaliação deste protocolo. Não há resultados v2.

## Objetivo e unidade

Pergunta de pesquisa proposta: como recuperação por similaridade e seleção enriquecida por temas se comparam na cobertura de aspectos específicos, fidelidade às evidências e formulação de hipóteses de melhoria quando cada consulta analisa um único produto?

A unidade é um produto explicitamente delimitado ou um kit, podendo reunir versões e códigos de item da mesma linha identificável. Mudanças de fórmula, aplicador, tamanho e embalagem são mantidas como potenciais achados, não como motivo de exclusão. Cada consulta usa somente avaliações mapeadas ao produto; diferentes produtos de uma mesma marca/linha não são reunidos automaticamente. Preservar diferenças de versão, pessoa, compra anterior/atual e condição de uso quando explícitas, e declarar quando não são identificáveis.

O mapeamento candidato está em [product-scope-revised.md](product-scope-revised.md) e configs/product-focused-scope.draft.json: 15 casos com 3.784 avaliações e 59 avaliações de um item com identidade funcional pendente. Isso não fixa a quantidade final de casos. Os dados já foram explorados; não alegar teste novo intocado. Os conjuntos anteriores servem à descrição da origem, sem hipótese causal de variedade.

## Comparação dos métodos

| Etapa | Tradicional v2 | Temático v2 |
|---|---|---|
| Universo de busca | Todas as avaliações elegíveis da produto escolhido | Mesmo universo |
| Preparação | Mesma limpeza, segmentação e embeddings | Mesma preparação |
| Candidatos | Mesma busca por similaridade e mesmo limite | Mesmos candidatos, com a mesma regra de relevância |
| Redundância | Mesma regra de deduplicação de trechos | Mesma regra |
| Seleção | Melhores candidatos por similaridade | Diversidade entre agrupamentos do produto, completando por similaridade |
| Resposta | Mesmo prompt, modelo, esquema, idioma e limites | Mesma configuração |
| Avaliação | Mesmas perguntas e referência por produto | Mesma referência, com revisão sem rótulo do método |

A diferença principal será a seleção das evidências, não prompt, modelo ou quantidade permitida. O temático não poderá preencher o contexto com evidências irrelevantes apenas para representar um grupo. Não garantir contraste positivo/negativo a um método apenas. Se houver expansão de consultas ou busca por aspectos, aplicar a mesma regra aos dois e decidir no desenvolvimento.

Os agrupamentos temáticos precisam ser recalculados dentro de cada produto, em destinos v2. Os grupos globais reaproveitados pela interface podem refletir diferenças entre produtos e não são agrupamentos locais validados. Vocabulário e exemplos representativos serão inspecionados; não chamar todo cluster de tema validado. Produtos sem estrutura de agrupamento útil devem ser documentadas, sem exclusão posterior por desempenho.

## Desenvolvimento e orçamento

Revisar a identidade das cinco famílias de desenvolvimento já separadas da avaliação e delimitá-las como produtos antes do piloto individual. Aplicar o mesmo critério de permitir versões do mesmo produto. Não ajustar usando as respostas finais dos candidatos de avaliação. O desenvolvimento anterior também já foi inspecionado; não se trata de validação independente.

Executar em fases pequenas: verificar relevância/atribuição e agrupamentos locais; testar orçamentos de 8, 12 e 16 trechos dentro da janela real do modelo; verificar síntese e fidelidade. Oito é a referência operacional anterior, não uma quantidade comprovadamente suficiente. O número final e os limites de entrada/saída serão comuns aos métodos, definidos por capacidade e critérios de desenvolvimento antes da avaliação. Mais trechos não significam mais avaliações únicas nem maior profundidade. Registrar o que efetivamente coube no contexto.

Manter inicialmente Gemma 3 4B, encoder MiniLM e FAISS. Não trocar modelo e estratégia de recuperação simultaneamente. Selecionar parâmetros de agrupamento local no desenvolvimento, considerando tamanho mínimo dos grupos, coerência semântica e redundância; não transportar automaticamente os seis grupos da v1 para cada produto. Controlar duração e falhas para evitar repetir uma grande grade pouco informativa.

A resposta em português terá achados pequenos, observação, condições explicitamente relatadas, divergências quando houver apoio, proposta quando solicitada, incertezas e referências por achado. Não inferir condições ausentes nem transformar experiência com outro produto em problema do produto analisado. Esse contrato é da v2; o prompt inglês da v1 permanece preservado. A estratégia de idioma da busca também será registrada e comum aos métodos, sem presumir que um encoder em inglês mantenha a mesma qualidade para perguntas em português.

## Perguntas e referências

Proposta de seis tarefas por produto, adaptando somente a função do produto antes de congelar:

1. Quais dificuldades de aplicação, operação ou remoção são relatadas? Em quais condições explicitadas ocorrem?
2. Quais limitações de desempenho ou duração são descritas? Distinguir duração do efeito, vida útil e quantidade do conteúdo conforme aplicável.
3. Que experiências divergem sobre um mesmo aspecto e que mudanças de fórmula, aplicador ou embalagem são relatadas? Preservar a atribuição e não inventar uma explicação ou ligação causal entre mudança e resultado.
4. Que problemas de embalagem, conservação ou informação do produto aparecem, distinguindo relatos de suspeitas sobre causa?
5. Que melhorias poderiam ser investigadas a partir dos problemas documentados e quais qualidades valorizadas precisam ser preservadas? Separar evidência, proposta e validação.
6. Esses relatos permitem prever qual mudança aumentaria as vendas? Explicitar o limite sem impedir a formulação de hipóteses apoiadas.

Perguntas sem apoio precisam de referência de insuficiência ou denominador indisponível, conforme protocolo. Não inventar uma divergência para cumprir a pergunta. As tarefas não devem ser ajustadas depois de ler as respostas finais de um método.

Reaproveitar as interpretações humanas anteriores como material inicial, não como referência v2 automaticamente aprovada. Preparar uma referência por produto/pergunta, antes da geração final, contendo aspectos, condições, diferenças materiais de versão/experiência, contrastes documentados e vínculos de apoio locais. O procedimento de construção e a extensão da leitura devem ser registrados; a referência continua parcial se não houver anotação exaustiva. Concordar com uma interpretação não certifica um novo denominador ou concordância entre avaliadores.

## O que será medido

Profundidade será operacionalizada por componentes separados, sem nota composta:

- Cobertura de aspectos específicos da referência, na recuperação e na resposta.
- Cobertura de condições/qualificações e contrastes documentados quando elegíveis, com denominadores próprios; apoio ausente é indisponível, não zero por padrão.
- Fidelidade de afirmações, incluindo atribuição ao produto, versão, pessoa e produto anteriormente usado; contar omissões separadamente de contradições e falta de suporte.
- Propostas: vínculo com problema/evidência, separação entre relato e hipótese, pertinência e validação explícita, reportados separadamente.
- Avaliações únicas recuperadas, incluídas e citadas; trechos por avaliação e redundância. Mais citações não prova apoio ou representatividade.
- Latência, tokens e falhas. Tempo de preparação/agrupamento separado da consulta; sem monitoramento de memória, processos, CPU ou energia.

Critérios semânticos, exemplos e regras de pontuação serão escritos e calibrados no desenvolvimento antes de congelar. Respostas longas ou com mais citações não recebem crédito por profundidade automaticamente. Validade do JSON não significa fidelidade. Saídas vazias, cortes e erros serão mantidos, sem regenerar para escolher a melhor resposta; definir os denominadores para falhas antes da execução.

## Escala e critérios de aceite

A quantidade de produtos, perguntas e repetições será fechada após o piloto e a construção de referências. As seis tarefas são uma proposta; não há grade final autorizada nem necessidade de manter todos os 15 candidatos. Registrar o tamanho final antes da avaliação, sem ampliar ou selecionar casos em função do método vencedor. Não repetir automaticamente a grade de sensibilidade anterior.

Antes da avaliação: testes de isolamento do produto e de pertencimento dos itens; identidade de candidatos e orçamento entre métodos; citações vinculadas aos trechos corretos; tratamento de trechos da mesma avaliação; registro de prompts/modelos/fontes; verificação de saídas completas no desenvolvimento e inspeção semântica de falhas. Passar testes mecânicos não é evidência de qualidade da resposta. Eventual falha posterior permanece no resultado.

Depois: todas as tentativas mapeadas, falhas preservadas, anotações completas segundo a rubrica v2, selagem anterior à comparação e exportação reproduzível. Reportar primeiro cada produto e depois médias com pesos iguais entre produtos; não deixar um produto com muitas avaliações dominar a média. Comparar métodos de forma pareada; perguntas e repetições são dependentes. Incerteza entre produtos, se estimada, será exploratória, considerando poucos produtos e seleção intencional; não tratar afirmações ou trechos como réplicas independentes.

A revisão humana deve ser delimitada antes de pedir trabalho à usuária: exemplos de calibração e uma amostra cega estratificada, com quantidade e carga estimadas após conhecer o tamanho das fichas. Não exigir revisão de todas as tentativas, não assumir que assistente e usuária são avaliadores independentes e não alegar validação humana integral. Sem avaliador independente, manter essa limitação explícita.

## Reuso, reconstrução e preservação

| Reaproveitar | Preparar novamente para v2 |
|---|---|
| Fonte local, limpeza e auditoria de privacidade documentadas | Manifestos e corpora/índices por produto com hashes e destinos novos |
| Avaliações elegíveis e famílias de desenvolvimento separadas | Agrupamentos locais e seleção de parâmetros no desenvolvimento |
| Encoder e vetores existentes, se sua identidade e segmentação forem verificadas | Perguntas, referências e denominadores por produto |
| Gemma, FAISS, mecanismos de citação e testes úteis | Contrato de geração e rubrica de profundidade em português |
| Interface e seleção por produto como ponto de partida | Runner v2, congelamento, novas gerações, anotações e métricas |
| Histórico, resultados, referências e arquivos congelados v1 | Discussão e conclusões adicionais baseadas em resultados v2 reais |

Criar módulos/configurações e diretórios v2 sem editar fontes/configurações necessárias à reprodução v1. Preservar métricas e conclusões v1 como etapa anterior. Não juntar tentativas novas às anteriores numa nota única.

O contraste v1 versus v2 será uma evolução documentada, não efeito causal isolado do recorte por produto: idioma, referência, agrupamento e geração também podem mudar. Para atribuir especificamente o ganho ao foco individual, seria necessária uma ablação separada mantendo os demais fatores constantes, planejada antes dos resultados; não é requisito desta primeira extensão.

## Sequência proposta

1. Alinhar este desenho e as seis tarefas.
2. Preparar piloto individual nos produtos de desenvolvimento, medindo falhas, relevância e capacidade de contexto.
3. Escolher configuração compartilhada e construir referências/rubrica, com revisão humana delimitada.
4. Congelar v2 e implementar/verificar a execução reproduzível separada.
5. Executar, anotar sem rótulos de método, calcular e discutir, inclusive se não houver melhora.

Nenhum ganho de profundidade é pressuposto. Não criar repositório remoto nem publicar sem revisão e autorização da usuária.
