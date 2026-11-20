# Perguntas de avaliação — versão com 14 perguntas

Estrutura alinhada: 12 perguntas de análise e duas de controle, aplicadas separadamente aos três conjuntos. A redação está apresentada para revisão; referências e parâmetros ainda precisam ser congelados. As versões anteriores de 16 e oito perguntas foram preservadas como histórico. Configuração atual: configs/questions.eval.14.draft.json; plano: configs/benchmark-plan.draft.json.

Regra comum: usar somente as avaliações fornecidas, citar evidências para afirmações factuais e atribuir cada achado à família correta. Separar produtos e versões, experiências diretas e indiretas, relatos e hipóteses. Declarar insuficiência de evidência; não inferir prevalência populacional dos trechos recuperados nem transferir benefícios animais para humanos. As perguntas executadas estão em inglês; abaixo está a redação equivalente em português.

## Q01 — Análise

Quais dificuldades os consumidores relatam na aplicação, remoção ou manuseio dos produtos, e como elas afetam a rotina de uso? Exclua problemas específicos da embalagem.

## Q02 — Análise

Quais limitações de desempenho são relatadas em relação à função dos produtos e às condições de uso mencionadas? Não inclua aqui duração do efeito, rendimento ou vida útil.

## Q03 — Análise

Quais experiências negativas relacionadas a cheiro, textura, sensação durante o uso ou desconforto são relatadas? Descreva as percepções sem diagnosticar causas ou condições médicas.

## Q04 — Análise

O que os consumidores relatam sobre duração do efeito, rendimento até o produto acabar, autonomia entre recargas ou trocas de pilhas e vida útil até falhar? Distinga esses conceitos conforme o tipo de produto e indique quando faltarem evidências.

## Q05 — Análise

Quais problemas de embalagem afetam proteção, conservação, abertura, fechamento ou dosagem dos produtos? Separe a condição recebida de uma causa ou responsabilidade que não esteja demonstrada.

## Q06 — Análise

Quais benefícios e características os consumidores valorizam nos produtos e que, por isso, merecem ser considerados ao planejar melhorias? Inclua motivos de recompra ou custo-benefício apenas quando explicitamente mencionados.

## Q07 — Análise

Quais características recebem tanto elogios quanto críticas dentro de uma mesma família de produto? Quais diferenças de preferência ou contexto de uso são explicitamente mencionadas? Não suponha causas nem segmentos demográficos.

## Q08 — Análise

Quais mudanças no produto ou na embalagem são explicitamente solicitadas pelos consumidores? Diferencie pedidos de simples reclamações e não acrescente propostas próprias.

## Q09 — Análise

Que melhorias físicas ou funcionais no produto ou na embalagem podem ser propostas a partir dos problemas relatados? Para cada proposta, separe problema observado, melhoria sugerida, benefício esperado e o que precisaria ser verificado. Exclua mudanças apenas de comunicação.

## Q10 — Análise

Que tensões entre características desejadas aparecem nas avaliações, e que benefícios valorizados poderiam ser afetados por mudanças voltadas às reclamações? Separe relações explicitamente relatadas de possíveis compromissos ainda hipotéticos, sem inventar restrições técnicas.

## Q11 — Análise

Quais diferenças os consumidores relatam entre o que esperavam ou entenderam da descrição dos produtos e a experiência recebida? Trate a descrição ou promessa como relatada pelo consumidor quando ela não estiver disponível para verificação.

## Q12 — Análise

Que melhorias nas instruções, descrições ou informações dos produtos poderiam tratar dúvidas e expectativas não atendidas relatadas pelos consumidores? Separe a evidência da dúvida ou confusão, a proposta de informação e o que ainda precisaria ser verificado.

## Q13 — Controle

Estas avaliações permitem determinar qual mudança nos produtos aumentaria as vendas? Explique o que as evidências permitem concluir e o que seria necessário verificar para sustentar essa previsão.

## Q14 — Controle

Estas avaliações permitem garantir que os produtos são seguros para todos os consumidores? Explique o que os relatos permitem concluir e os limites dessa conclusão, sem diagnósticos ou garantias médicas.

## Critérios e limites

Avaliar separadamente cobertura da referência auditada na recuperação e na resposta, sustentação das afirmações e atribuição correta às famílias. Propostas inferidas não exigem uma solução única: avaliar vínculo com problemas documentados, clareza das hipóteses e limites. Pedidos explícitos exigem linguagem de solicitação, não apenas insatisfação. Não inferir que repetir um tema em perguntas relacionadas produz observações independentes.

Q01 trata do processo de uso; Q02 do resultado percebido; Q03 das percepções sensoriais e desconforto; Q04 das diferentes durações. Q05 trata de embalagem. Q06 identifica benefícios a preservar e Q07 integra experiências contrastantes. Q08 exige pedidos explícitos; Q09 propõe melhorias; Q10 examina tensões e possíveis perdas. Q11 diagnostica expectativas e Q12 propõe informação para tratá-las. Quando uma evidência atender a mais de uma tarefa, a reutilização é permitida sem confundir os critérios.

Q13 e Q14 verificam extrapolação sobre vendas e segurança. Espera-se reconhecer que relatos não sustentam previsões causais de vendas ou garantias universais de segurança; não se exige rejeitar toda informação útil dos relatos. Reportar os controles separadamente da cobertura das 12 perguntas de análise. Essas duas perguntas são controles explícitos de limites, não testes validados de resposta factual ausente. Uma futura avaliação desse último tipo exigiria conferir a ausência da resposta no corpus antes de acrescentar casos.

São 42 combinações pergunta/conjunto por método e repetição. Não são 42 conjuntos independentes; repetições medem variabilidade de execução. As perguntas de síntese mais amplas devem ter orçamento comparável de contexto e resposta entre métodos, escolhido apenas no desenvolvimento.

Foram preparados 42 espaços privados vazios de referência vinculados aos hashes dos corpora atuais. Nenhuma resposta ou referência foi inventada; não houve execução final. O protocolo de construção de referência descrito em docs/benchmark-review-proposal.md continua aplicável, substituindo sua lista antiga de oito perguntas por esta lista de 14.

## Referências consolidadas em revisão

Os três pacotes propostos estão em docs/reference-packet-1.md, docs/reference-packet-2.md e docs/reference-packet-3.md. Cobrem 42 casos com evidências privadas vinculadas ao corpus. São referências auditadas não exaustivas; aprovação e denominadores ainda não estão congelados. Dez unidades de Q01 do conjunto compacto já tinham aprovação e foram preservadas. Ver docs/consolidated-reference-progress.json.

## Correção de cobertura por família

A referência atual em revisão é a matriz de 14 perguntas × cinco famílias de cada conjunto (210 células). Ver docs/family-reference-matrix-progress.json e docs/reference-packet-1-revised.md, reference-packet-2-revised.md e reference-packet-3-revised.md. Status distinguem evidência direta, contexto positivo, insuficiência na inspeção, hipótese e controle. Não equivalem a anotação exaustiva ou denominadores congelados.
