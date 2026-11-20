# Discussão e conclusões do TCC

Texto integrado aos resultados da avaliação principal e da análise de sensibilidade v1. Os valores vêm dos [agregados principais](primary-evaluation-results.v1.json) e dos [agregados de sensibilidade](sensitivity-results.v1.json); os respectivos relatórios documentam denominadores, regras e procedimentos. As duas etapas são analisadas separadamente, sem uma média conjunta das 1.008 tentativas.

## Discussão

### Cobertura temática e fidelidade respondem a questões distintas

O objetivo do estudo foi investigar se a seleção de evidências diversificada por agrupamentos temáticos poderia apoiar a identificação de oportunidades de melhoria em produtos, em comparação com a recuperação por similaridade. Na configuração avaliada, o enriquecimento ocorre na seleção das passagens: os dois métodos compartilham modelo gerador, embeddings, conjunto de candidatos, prompt e orçamento de contexto. Os resultados permitem examinar essa estratégia específica, sem representar todas as formas possíveis de RAG enriquecido.

Na avaliação principal, o método temático apresentou maior fidelidade média nos três estudos de caso: 84,7% contra 79,0% em máscaras, 81,5% contra 71,4% no capilar e 81,6% contra 75,4% no variado. Entretanto, a cobertura da resposta foi menor em máscaras (6,7% contra 13,7%) e maior no capilar (17,1% contra 12,8%) e no variado (4,7% contra 3,3%). Assim, maior proporção de afirmações sustentadas não implicou cobertura mais ampla dos aspectos da referência. Uma resposta pode manter fidelidade ao discutir poucos relatos e ainda deixar de incorporar aspectos relevantes.

Os intervalos exploratórios de diferença de cobertura incluem zero ou têm zero no limite nos três casos. Apenas a diferença de fidelidade no capilar teve intervalo inteiramente positivo: +10,1 pontos percentuais, com intervalo de +0,6 a +21,0. Esse resultado localizado deve ser interpretado com cautela, considerando a dependência entre perguntas, a referência parcial e a anotação assistida. Ele não estabelece superioridade geral do método nem efeito causal da variedade dos produtos.

### A sensibilidade limita a estabilidade dos ganhos observados

A grade secundária compreendeu 27 cenários, combinando três conjuntos, três tamanhos de amostra e três sementes, com uma repetição por cenário. Nas nove combinações de conjunto e tamanho, a diferença média de cobertura da resposta favoreceu o temático em quatro, o tradicional em quatro e foi nula em uma. A diferença de fidelidade foi positiva para o temático em quatro grupos e negativa em cinco. Portanto, a maior fidelidade temática da etapa principal não se manteve de forma estável quando o corpus recuperável mudou.

Há exemplos de perdas consistentes entre as três sementes dentro de uma combinação. No capilar com 40 avaliações por família, a diferença de cobertura da resposta foi de −15,48 pontos percentuais em média, variando de −21,43 a −8,33. Em máscaras com 60 avaliações por família, a diferença também foi negativa nas três sementes: média de −4,31 pontos percentuais. Em contrapartida, o variado com 20 avaliações por família teve ganho médio de +3,33 pontos percentuais, decorrente de uma semente positiva e duas empatadas. Essas amplitudes descrevem as sementes observadas e não são intervalos de confiança ou evidência de um efeito populacional.

A disponibilidade das unidades de referência muda entre os subconjuntos. Há 58 combinações de pergunta e subconjunto sem apoio conhecido, cuja cobertura permanece indisponível. A expansão do corpus pode acrescentar tanto evidências recuperáveis quanto unidades ao denominador; a comparação direta das porcentagens entre tamanhos não isola o efeito do volume. Os subconjuntos menores estão contidos nos maiores para a mesma semente, e os cenários não são réplicas independentes.

A distinção entre recuperação e resposta ajuda a localizar uma dificuldade do pipeline. Em máscaras com 20 avaliações por família, o temático ganhou 9,88 pontos percentuais de cobertura na recuperação, mas perdeu 0,46 ponto na resposta. A presença de uma evidência no contexto não garante sua incorporação correta pelo gerador. Uma interpretação possível é que diversificar grupos vetoriais não assegura a seleção dos aspectos exigidos por cada pergunta nem sua síntese no orçamento disponível. O experimento não separa esses mecanismos, de modo que essa explicação permanece hipótese para investigação.

### Utilidade para oportunidades de melhoria em produtos

A aplicação pretendida requer transformar experiências de consumidores em hipóteses de melhoria vinculadas a problemas e famílias identificáveis. Fidelidade, cobertura e utilidade da proposta são requisitos complementares. Na sensibilidade, o critério de vínculo da proposta a problema e família sustentados foi atendido em média em 63,0% no tradicional e 58,0% no temático. A distinção entre relato e proposta alcançou 75,3% e 79,0%, respectivamente. A pertinência à tarefa foi de 33,3% em ambos, e a explicitação de incertezas e validação foi de 70,4% em ambos. Os critérios são separados; não compõem uma nota geral de qualidade.

Esses resultados indicam dificuldade de atender integralmente à pergunta, mesmo quando parte da resposta contém observações ou sugestões úteis. Como os critérios são binários para a resposta inteira, uma violação material pode impedir crédito apesar de haver uma ideia pertinente em outra família. As taxas não significam que todas as demais sugestões sejam inúteis. Também não foi medida a viabilidade técnica, a aceitação das propostas por equipes de produto ou seu efeito comercial.

As avaliações permitem formular hipóteses sobre desempenho, aplicação, embalagem e comunicação de atributos, preservando a atribuição ao relato original. A ausência de informações de vendas não impede propor uma hipótese de melhoria. Contudo, uma reclamação não demonstra sua frequência na população, uma comparação com produto mais barato não prova perda de vendas, e um sintoma relatado não comprova causalidade ou risco clínico. A proposta deve ser apresentada como hipótese apoiada por evidências e sujeita a validação adequada ao problema.

Nos controles de sensibilidade, ambos os métodos evitaram garantias ou previsões causais injustificadas em todas as respostas; o reconhecimento explícito do limite epistêmico foi de 100% no tradicional e 98,1% no temático. Isso descreve o atendimento aos critérios dessas perguntas, sem certificar segurança dos produtos ou ausência de erros em outras partes das respostas. A utilidade prática permanece condicionada à conferência das fontes e à revisão das hipóteses antes de decisões de produto.

### Latência, tokens e falhas operacionais

Na etapa principal, o temático teve menor mediana de tempo em máscaras e maior nos conjuntos capilar e variado. Na sensibilidade, sua mediana foi maior nos nove grupos. Houve 564.805 tokens de entrada e 182.636 de saída informados para o tradicional, contra 565.257 e 190.270 no temático. A chamada com falha no tradicional não informou tokens; esses totais incluem apenas medições disponíveis. Comprimento das respostas, ordem fixa de execução, aquecimento e carga compartilhada limitam a atribuição das diferenças de tempo exclusivamente à seleção temática.

A sensibilidade preservou uma falha de chamada, 42 respostas com formato inválido e 34 cortes pelo limite de geração. Essas ocorrências podem se sobrepor e não representam categorias somáveis de tentativas distintas. Na etapa principal, foram preservadas 12 saídas cortadas, sem falhas de chamada. A retenção das ocorrências evita descrever somente as respostas bem-sucedidas. A resposta vazia da sensibilidade não recebeu fidelidade artificial de 100%: ficou sem métrica de afirmações e com a tarefa de proposta não atendida.

A avaliação computacional se restringe a tempos de parede e tokens informados pelo Ollama. Não foram medidos memória, uso de CPU, energia, operações computacionais ou custo monetário. Portanto, o trabalho pode discutir latência e volume de tokens nesta execução local, mas não concluir qual arquitetura é universalmente mais barata ou eficiente.

### Limitações e alcance das conclusões

A avaliação utiliza três estudos de caso, com cinco famílias operacionais cada, e uma configuração de Gemma 3 4B local. Há apenas um conjunto por condição de variedade; categoria, composição, volume e características dos relatos variam simultaneamente. As famílias também podem reunir versões diferentes. Não é possível atribuir as diferenças observadas apenas à variedade ou generalizar para outros produtos, idiomas, modelos e estratégias de recuperação.

A referência de 179 unidades factuais foi auditada, mas não é exaustiva nem independente. Cobertura é a proporção de aspectos elegíveis dessa referência, e não de todos os temas existentes nas avaliações. Uma cobertura baixa não demonstra ausência de qualquer insight útil. A procedência exata do Parquet fornecido em relação ao arquivo oficial declarado como Amazon Reviews 2023 All_Beauty ainda exige verificação; o esquema compatível não resolve essa limitação.

A revisão humana abrangeu interpretações de uma amostra de 18 itens principais e cinco de calibração, acompanhadas da interpretação do assistente. A anotação formal e sua operacionalização numérica foram realizadas pelo assistente; a sensibilidade não teve nova pontuação humana independente. Não foi medida concordância entre avaliadores. Fichas sem rótulo do método e selagem anterior à comparação favorecem rastreabilidade, mas não eliminam possíveis vieses ou erros de anotação.

A divisão das respostas em unidades de afirmação depende de frases, conjunções e contexto, limitando a interpretação da fidelidade. Perguntas tematicamente dependentes, três repetições na etapa principal, uma na sensibilidade e subconjuntos aninhados limitam as inferências estatísticas. Os intervalos bootstrap são exploratórios. A reprodução idêntica dos agregados e os 57 testes de software verificam procedimentos de cálculo e integridade, sem validar independentemente os julgamentos semânticos ou a qualidade dos insights.

## Conclusões

O trabalho implementou e avaliou um pipeline local para investigar oportunidades de melhoria em produtos a partir de avaliações de consumidores, comparando recuperação por similaridade com seleção diversificada por agrupamentos temáticos. A contribuição consiste na comparação reproduzível sob configuração comum, na avaliação separada de cobertura, fidelidade, propostas e controles e no registro de latências, tokens, falhas e limites de evidência.

Os resultados não demonstraram vantagem consistente do enriquecimento temático na configuração estudada. A maior fidelidade média observada nos três casos principais não se mostrou estável na análise de sensibilidade, e a cobertura apresentou ganhos e perdas conforme conjunto, tamanho e semente. A diversificação das evidências também não garantiu que os aspectos recuperados fossem incorporados à resposta. Esses achados respondem à questão de pesquisa sem confirmar uma superioridade geral de qualquer método.

Para a identificação de oportunidades de melhoria, o pipeline pode organizar evidências e apoiar a formulação de hipóteses, mas sua utilidade decisória não foi validada com equipes de produto ou resultados comerciais. As propostas precisam preservar a ligação com o problema relatado, explicitar incertezas e ser submetidas a revisão. O cumprimento dos controles não substitui essa revisão, e opiniões dos consumidores não constituem comprovação técnica, clínica ou causal.

Como continuidade, recomenda-se priorizar anotação independente de uma amostra estratificada, com análise de divergências, e expansão da referência para reduzir lacunas. Em experimentos futuros, a recuperação pode ser avaliada quanto à relevância específica para a pergunta, à redundância e à cobertura de famílias, comparando estratégias de diversidade e o aproveitamento das passagens pelo gerador. Mudanças de prompt ou seleção devem formar uma nova versão experimental, com desenvolvimento separado e nova avaliação, preservando os resultados congelados. A validação das hipóteses com especialistas e usuários finais permitiria estudar utilidade e viabilidade além das métricas textuais.

A conclusão se limita aos dados, às referências, aos julgamentos e à execução local documentados. O estudo oferece evidências de que acrescentar diversidade temática à seleção do contexto, por si só, não assegura respostas mais completas ou mais fiéis nas condições avaliadas.
