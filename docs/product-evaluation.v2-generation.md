# Geração da avaliação por produto — v2 congelada

A configuração foi congelada após autorização da usuária. O manifesto `configs/evaluation-freeze.v2.json` vincula por hashes os 73 arquivos de entrada, código e verificações técnicas. O nome histórico `product-evaluation.v2.approved-not-frozen.json` foi preservado: o manifesto externo registra o congelamento e a autorização da execução.

## Grade executada

Foram analisados separadamente GranNaturals, Pure Body Naturals e Bold Lash, com temas internos a cada produto. Cada produto tem seis perguntas e dois métodos, totalizando 36 respostas principais em inglês (18 por método). As 24 execuções adicionais de Q1/Q5 são diagnósticos de estabilidade; não substituem respostas principais nem ampliam o denominador de qualidade. As 36 respostas principais receberam tradução automática separada para apresentação em português.

Foram mantidos o Gemma 3 4B local, o gerador original em inglês, os contextos de oito avaliações, a busca por aspectos, os parâmetros e os denominadores aprovados. Não houve reparo, nova tentativa ou seleção da melhor resposta.

## Verificações da rodada

- 60/60 gerações em inglês com formato válido, sem erros de execução e sem cortes pelo limite de tokens.
- 36/36 traduções com formato válido, sem erros de execução e sem cortes pelo limite de tokens.
- Inglês original preservado após a tradução, conferido por hash em cada vínculo.
- 73 arquivos congelados e 77 arquivos anteriores de preservação conferidos sem alterações.
- Contextos, respostas, traduções e registros individuais permanecem nos diretórios locais ignorados pelo Git.

A validade de formato não estabelece fidelidade, profundidade, cobertura ou utilidade das sugestões. A equivalência de traduções também exige revisão semântica. Não foi calculado resultado de qualidade nem declarado método vencedor.

## Medições operacionais

As medianas de geração das 18 respostas principais por método, incluindo as verificações do executor, foram 5,92 s no tradicional e 5,46 s no temático. São medições desta máquina e desta execução; cache e ordem de chamadas limitam sua interpretação. Tradução, sondagens técnicas de orçamento e repetições diagnósticas têm custos registrados separadamente, sem serem incorporados à qualidade das respostas principais. Não foram estimados consumo energético ou custo monetário.

Das 24 repetições diagnósticas, 18 reproduziram exatamente o inglês principal e seis diferiram, apesar de manterem o contexto na mesma ordem. As diferenças ficam preservadas para inspeção; identidade textual não comprova qualidade.

Os agregados completos, tokens, tempos e diagnóstico de estabilidade estão em [product-evaluation.v2-generation-summary.json](product-evaluation.v2-generation-summary.json). O relatório pode ser conferido novamente com `scripts/report_product_generation_v2.py`, escolhendo novos destinos de saída; ele não chama o modelo nem atribui notas semânticas.

## Próxima etapa

Anotar as respostas originais em inglês conforme a rubrica congelada, com os métodos ocultos nos formulários, e aplicar a revisão humana parcial planejada de 12 respostas (seis pares). A referência é parcial e a anotação assistida não equivale a avaliação independente. Só após completar e validar essas anotações serão exportadas as métricas semânticas e atualizadas a discussão e as conclusões da v2. Os resultados anteriores continuam identificados como anteriores.
