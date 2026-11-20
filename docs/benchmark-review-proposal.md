> Histórico: a proposta de oito perguntas foi substituída pela estrutura de 14 em docs/benchmark-questions-14.md e configs/benchmark-plan.draft.json. O protocolo de referência abaixo permanece aplicável; números e lista antiga não são a versão atual.

# Perguntas e referência de avaliação — proposta para alinhamento

Versão proposta, não congelada. O rascunho original de 16 perguntas foi preservado. A nova proposta tem seis perguntas de análise e duas de controle, aplicadas separadamente aos três conjuntos: 24 combinações pergunta/conjunto, por método e repetição. Elas não são 24 conjuntos independentes; as repetições também não são julgamentos humanos independentes.

## B01 — diagnosis

Quais problemas de uso, desempenho ou experiência sensorial são relatados, e quais consequências têm para o uso do produto?

## B02 — packaging

Quais problemas de embalagem ou apresentação do produto são relatados, e como afetam sua utilização ou conservação?

## B03 — strengths_and_contrasts

Quais características são valorizadas ou recebem opiniões divergentes, e que preferências ou condições de uso são explicitamente mencionadas?

## B04 — explicit_opportunities

Quais mudanças no produto ou na embalagem são explicitamente solicitadas pelos consumidores? Não acrescente propostas próprias.

## B05 — inferred_opportunities

Que melhorias físicas ou funcionais no produto ou na embalagem podem ser propostas a partir dos problemas relatados? Separe problema observado, proposta, benefício esperado e incertezas, incluindo características valorizadas que poderiam ser afetadas.

## B06 — communication_opportunities

Que melhorias nas instruções ou informações do produto poderiam tratar dúvidas e diferenças entre expectativas e experiência relatada? Separe evidências, propostas e informações que ainda precisariam ser verificadas.

## B07 — limits_sales

Estas avaliações permitem determinar qual mudança aumentaria as vendas? Explique o que as evidências permitem e não permitem concluir.

## B08 — limits_safety

Estas avaliações permitem garantir a segurança dos produtos para todos os consumidores? Explique os limites das evidências, sem conclusões médicas.

## O que muda

B01 reúne dificuldades, desempenho, aspectos sensoriais e consequências para o uso. B03 reúne benefícios e opiniões divergentes; custo-benefício entra quando for explicitamente mencionado, sem pergunta própria. B05 inclui possíveis compromissos entre melhorias e benefícios existentes. B06 reúne expectativas, instruções e lacunas necessárias para verificar as propostas. Recompra, abandono e limitações aparecem quando pertinentes, sem perguntas repetitivas.

A redução simplifica a revisão, mas as perguntas ficam mais amplas. Conferir no desenvolvimento se o orçamento de contexto e resposta é suficiente para ambos os métodos, congelando-o antes da avaliação. A proposta não representa tamanho de benchmark validado estatisticamente.

B07 e B08 avaliam reconhecimento de limites. Reportar seus resultados separadamente: não combiná-los com a cobertura temática das seis perguntas de análise para inflar uma média global.

## Como construir a referência

Após alinhamento das perguntas, criar unidades de referência por pergunta, conjunto e hash do corpus. Cada unidade terá família, aspecto, descrição fiel, IDs de avaliações de apoio e limites de interpretação. Em propostas de melhoria, distinguir o problema documentado da solução inferida, aceitando alternativas justificadas em vez de exigir uma redação ou solução única. Solicitações explícitas não podem ser preenchidas com propostas inferidas.

Construir a referência antes de ler as respostas finais dos métodos. A fonte deve ser uma seleção sistemática de evidências do corpus e inspeção de casos, sem depender exclusivamente dos primeiros resultados de um dos recuperadores ou dos clusters do método temático. Declarar a cobertura da inspeção; se não for exaustiva, chamar a métrica de cobertura da referência auditada, não cobertura de todos os temas possíveis do corpus.

Para cada resposta, registrar unidades de referência cobertas, afirmações factuais, sustentadas, contraditas e sem suporte. Checar se a citação realmente sustenta a afirmação e se pertence à família correta. Descrever avaliações de outras pessoas e de produtos anteriores como tais. Propostas plausíveis não são fatos nem resultados comprovados.

Cobertura = unidades pertinentes cobertas / unidades pertinentes da referência auditada. Fidelidade = afirmações factuais sustentadas / afirmações factuais totais. Quando não houver denominador, registrar não aplicável, sem atribuir zero ou um automaticamente. Em B04, ausência de solicitação explícita pode exigir abstenção correta; não inventar pedidos para produzir cobertura. Para B07/B08, registrar reconhecimento correto do limite e eventuais extrapolações, sem conclusões médicas ou causais sobre vendas.

As unidades de referência devem ser conferidas nos subconjuntos menores antes de calcular cobertura. Distinguir ausência de evidência no subconjunto de omissão na resposta. Não transportar automaticamente o denominador do corpus completo.

Ocultar método e ordem na revisão das respostas, mantendo a chave privada. Como a usuária conhece a construção do projeto, não declarar cegamento completo nem independência que não existe. Revisão adicional por outra pessoa é opcional; só calcular concordância se houver anotações independentes reais.

## Estado atual

Foram preparados o rascunho revisado, o plano e 24 espaços privados vazios para referências vinculadas aos hashes atuais. Nenhuma unidade de referência foi inventada ou aprovada. Não foram geradas respostas finais. Dados e anotações por registro permanecem fora do Git. Após alinhamento, preparar um pequeno bloco de unidades de referência para revisão, mantendo prompts e hiperparâmetros finais fora do ajuste por resultados de avaliação.
