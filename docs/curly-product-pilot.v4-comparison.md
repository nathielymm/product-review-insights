# Curly Co.: quarta rodada, com análise isolada de cada fonte

Estado: quatro respostas compostas a partir de 32 chamadas por fonte, preservadas com as três rodadas anteriores. A vinculação técnica das fontes foi verificada. A conferência semântica continua encontrando erros; o piloto não é configuração final aprovada nem avaliação independente.

## Ajuste implementado

A recuperação da terceira rodada foi mantida exatamente por pergunta/método: mesmo corpus, candidatos, trechos e ordem. Permaneceram 804 avaliações, 805 trechos, os quatro grupos locais, a busca por aspectos, modelo/digest, runtime e limites de contexto. O executor recusa executar se candidatos ou conteúdo divergirem da rodada 3.

A geração agora analisa cada uma das oito avaliações em uma chamada independente, sem histórico de outras avaliações. A aplicação fixa a fonte de cada resultado; o modelo não escolhe um identificador e não escreve o texto exibido como fonte. As chamadas usam o mesmo prompt e formato nos dois métodos. Os campos são relato, suspeita, melhoria e validação. O campo de suspeita deve registrar somente hipótese explícita do consumidor; melhorias continuam sendo hipóteses, não causas comprovadas.

A resposta final é uma composição determinística na ordem do contexto, sem outra síntese pelo modelo, tradução, reparo ou escolha manual dos melhores achados. Todos os resultados válidos e não vazios são apresentados. Chamadas inválidas, vazias, cortadas ou com erro permanecem registradas por fonte; não há nova tentativa automática.

Isso implica mudanças de arquitetura e de custo: oito chamadas e até oito achados por resposta, contra uma chamada e até seis achados antes. O teto planejado de saída total permaneceu em 1.536 tokens, distribuídos em 192 por fonte. O prompt é repetido e o custo de entrada cresce; não é o mesmo trabalho computacional. O limite do campo relato passou de 260 para 160 caracteres, com problemas de frases incompletas observados abaixo. Não se pode atribuir o resultado apenas à vinculação da fonte.

## Resultado mecânico e recursos

As 32 chamadas tiveram JSON válido, sem falha de API nem corte pelo limite de tokens. As quatro respostas têm oito achados e oito avaliações citadas. Essa maior contagem decorre também da remoção do teto de seis achados; não prova maior profundidade. Os trechos originais apresentados foram conferidos diretamente contra o contexto.

| Pergunta | Método | Chamadas: rodada 3 → 4 | Achados: rodada 3 → 4 | Tempo: rodada 3 → 4 | Tokens de entrada: rodada 3 → 4 |
|---|---|---:|---:|---:|---:|
| P01 | Tradicional | 1 → 8 | 6 → 8 | 5.25 → 9.05 s | 1672 → 4933 |
| P01 | Temático | 1 → 8 | 6 → 8 | 5.47 → 9.18 s | 1701 → 4962 |
| P02 | Tradicional | 1 → 8 | 6 → 8 | 7.10 → 10.96 s | 1272 → 4610 |
| P02 | Temático | 1 → 8 | 6 → 8 | 6.79 → 11.49 s | 1272 → 4610 |

Na execução inteira, os tokens de entrada passaram de 5.917 para 19.115, e os de saída de 1.745 para 2.285. São contagens observadas nesta execução, não custo monetário ou energia. Os tempos são de uma tentativa por combinação, em ordem fixa, sem controlar carga compartilhada; não sustentam inferência de latência típica ou superioridade. Não houve monitoramento de processos, memória ou CPU.

A conferência mecânica verifica que cada chamada recebe somente o texto de sua avaliação e que o resultado é vinculado ao seu identificador pelo sistema. Ela não estabelece que o modelo interpretou corretamente aquela avaliação. Uma afirmação pode continuar errada mesmo sem ter acesso às outras fontes.

## Comparação de significado com a rodada 3

### O que mudou favoravelmente nesta leitura

Na resposta tradicional à pergunta de melhorias, a proposta para a cabeça que se soltou passou a tratar da fixação cabeça-corpo do difusor. Na terceira rodada, a proposta tratava da conexão com o secador, outra interface mecânica. Essa correção apareceu nos dois métodos com a fonte correspondente nesta rodada.

O relato de quebra em dois meses não foi mais apresentado como quebra causada comprovadamente por peças coladas ou materiais ruins. A colagem apareceu como algo a verificar na proposta/validação, não como causa estabelecida no relato. Isso é um avanço pontual da leitura, sem representar validação de causa ou garantia de fidelidade geral.

As condições de pressão no couro cabeludo não foram novamente transferidas para a avaliação sobre viagem que antes recebia esse detalhe de outra fonte. Contudo, aquela avaliação ganhou outro erro de interpretação, descrito abaixo. O mecanismo impede selecionar o código de outra fonte, mas não impede inventar ou inverter conteúdo.

Na pergunta de melhorias, as avaliações finais sobre colapso durante movimento e sobre cabelo pesado/cacheado passaram a aparecer. Antes eram fornecidas, mas não citadas. Oito chamadas com oito espaços de achados também explicam essa diferença de inclusão; não deve ser tratada como ganho isolado de qualidade.

### Problemas que permanecem ou surgiram

- Um relato sobre o difusor anterior que veio com o secador foi apresentado como achado, sem identificar claramente que se tratava de outro produto. Na segunda pergunta, uma avaliação sobre substituir o difusor original foi interpretada como falha do produto atual. O erro de identidade intrarrelato continua, embora o código da fonte esteja fixo.
- A descrição de o produto ficar pequeno quando dobrado virou “após desdobrado”, e o tamanho compacto foi ligado causalmente ao amassamento no uso. A fonte oferece os dois aspectos, mas não sustenta essa inversão e explicação causal.
- A explicação do consumidor sobre silicone fraco/flexível continuou no relato como causa pouco qualificada. O campo separado de suspeita não foi preenchido de forma útil: recebeu palavras como “suspeita”, “vazia” e variações, em vez de hipótese explicitamente atribuída ou string vazia. Contar campos não vazios não mede suspeitas corretamente reconhecidas.
- Continuam propostas e verificações no campo de melhoria associadas a elogios, sem problema documentado do produto-alvo. Algumas são testes de validação de desempenho, não mudanças de produto; a distinção entre preservar uma qualidade e corrigir um problema permanece insuficiente.
- Vários relatos atingiram o limite de 160 caracteres; alguns terminam no meio de uma palavra ou ideia. Houve nove campos exatamente nesse limite, não nove cortes de tokens. O modelo completou o JSON, mas a frase pode estar incompleta. Formato válido e ausência de done_reason=length não significam texto completo.

A linguagem é predominantemente portuguesa, mas há palavras não traduzidas e frases malformadas. Não se declara qualidade linguística plena apenas porque o prompt pede português. A revisão foi do assistente, com os métodos visíveis e sem escore independente.

## Comparação entre os RAGs nesta arquitetura

Para as seis avaliações comuns à primeira pergunta, as saídas individuais foram idênticas entre métodos. Na segunda pergunta, as oito avaliações eram comuns e suas oito saídas também foram idênticas, mudando a ordem da composição. O modelo recebeu a mesma pergunta e uma fonte por chamada, sem conhecer o método ou as outras avaliações.

Isso é consistente com a diferença entre os métodos atuar na seleção das fontes. Não demonstra superioridade de um deles: quando selecionam as mesmas fontes, esta composição não fornece sínteses diferentes para comparar. A primeira pergunta ainda teve fontes diferentes entre métodos, mas os erros de interpretação impedem declarar um vencedor sem avaliação própria.

A separação por fonte reduz a possibilidade de fusão entre avaliações na geração, mas também retira a comparação conjunta de experiências do modelo. A resposta fica mais repetitiva e não constrói automaticamente uma síntese explícita das divergências. Esse é um custo funcional, além do aumento de chamadas e entrada.

## Conclusão de desenvolvimento

O vínculo técnico entre fonte e resultado ficou explícito e auditável, e houve correções pontuais em peças e causalidade. O objetivo semântico ainda não foi atingido de forma confiável: o sistema pode apresentar a fonte original correta para o código e uma interpretação errada para seu conteúdo.

A quarta rodada será preservada, sem promover automaticamente esta arquitetura à interface ou à avaliação final. Antes de ampliar produtos ou novas grades, é necessário tratar identidade dentro da própria avaliação, modalidade de hipóteses, propostas sem problema e limites de texto que produzam frases completas. Outra alteração exigirá nova versão/destino; nenhuma resposta foi corrigida para melhorar o resultado desta rodada.

## Preservação e reprodução

Os arquivos anteriores registrados antes da execução foram comparados por hash após o piloto. Configuração: configs/curly-product-pilot.v4-source-isolated.json. Executor: scripts/run_product_source_pilot.py. Resultados, chamadas e fontes individuais: results/product-pilot/curly-v4-source-isolated/, ignorado pelo Git.

Passaram 82 testes antes da geração e 83 na conferência final, incluindo orçamento agregado, fonte atribuída pelo sistema e verificação de que cada chamada recebe apenas sua avaliação. Esses testes não validam semântica. Os agregados foram reproduzidos com igualdade byte a byte sem nova geração.

```sh
.venv/bin/python scripts/report_product_source_pilot.py --output results/product-pilot/curly-v4-source-isolated/novos-agregados.json
```

O exportador exige as quatro respostas e preserva o destino existente. A execução também recusa sobrescrita. Falhas, cortes e saídas vazias devem continuar no registro; não escolher uma resposta melhor por repetição. Os agregados públicos não contêm textos ou anotações individuais.
