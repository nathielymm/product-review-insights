# Curly Co.: quinta rodada, comprimento e identidade do produto

Estado: quatro respostas compostas por 32 chamadas, comparadas à quarta rodada. Os contextos e a arquitetura isolada por fonte foram preservados. As frases ficaram mais completas nesta leitura, mas a distinção atual/anterior e a direção de condições continuam falhando. Não há validação de qualidade final ou vencedor.

## Ajustes e controles

O campo relato passou de 160 para até 480 caracteres, como margem de segurança, com orientação para uma frase completa de aproximadamente 20–35 palavras. Suspeita, melhoria e validação passaram de até 100 para até 160 caracteres. Os limites não são metas de preenchimento e não há corte de texto pelo código depois da geração.

Foi adicionado o campo referente, com produto_atual, comparacao_com_anterior e nao_identificado. O prompt orienta resolver pronomes e compras de substituição antes do resumo, não transferir defeitos de acessórios antigos, preservar aberto/dobrado e não transformar coexistência em causa. Melhorias ficam proibidas quando o modelo declara não identificar o produto. O rótulo é produzido pelo próprio modelo, não constitui verificação independente de sua interpretação.

Permaneceram a análise de uma avaliação por chamada, a fonte fixada pelo sistema, a composição determinística dos achados, as duas perguntas, as avaliações, índice, grupos, busca por aspectos, ranking/candidatos e ordem de fontes por pergunta/método. Modelo/digest, runtime e teto de saída de 1.536 tokens por resposta, dividido em 192 por fonte, são os mesmos da quarta rodada. O executor exige igualdade de candidatos e textos com ela. Não houve tradução, reparo de respostas, novas tentativas para substituir saídas ou reclassificação manual de rótulos.

## Resultados mecânicos

As 32 chamadas tiveram formato válido, sem falha de API ou corte por tokens. Cada resposta apresentou oito achados e oito avaliações citadas. O sistema apresentou os trechos originais; identidade do texto de fonte não significa que a interpretação esteja correta.

| Pergunta | Método | Maior relato nesta rodada | Relatos no limite de 160 antes | Relatos no novo limite de 480 | Tempo rodada 4 → 5 |
|---|---|---:|---:|---:|---:|
| P01 | Tradicional | 168 caracteres | 4 | 0 | 9.05 → 10.61 s |
| P01 | Temático | 174 caracteres | 5 | 0 | 9.18 → 10.92 s |
| P02 | Tradicional | 147 caracteres | 0 | 0 | 10.96 → 14.98 s |
| P02 | Temático | 147 caracteres | 0 | 0 | 11.49 → 14.93 s |

Na leitura qualitativa não foram observados os fragmentos interrompidos no meio de palavra/ideia que apareciam na rodada anterior. Não atingir o limite não prova, por si só, correção gramatical ou completude. Permanecem estrangeirismos, como “bouncy” e “flopava”, e algumas frases em primeira pessoa reproduzem a voz do consumidor sem atribuição clara.

Todos os 32 rótulos de referente foram produto_atual. Isso não demonstra identificação correta: houve uma atribuição errada a produto atual, descrita abaixo, apesar do rótulo válido. O teste automático valida enumeração e regras de campos, não verdade semântica.

O total de tokens de entrada passou de 19.115 para 24.395; os de saída, de 2.285 para 3.101. São medidas desta execução, com uma tentativa por combinação e ordem fixa. O teto planejado de saída não aumentou, mas o consumo observado e o prompt mudaram. Os tempos não sustentam generalização de latência ou superioridade. Não foram medidos memória, CPU, energia ou custo monetário.

## Comparação semântica com a quarta rodada

### Frases e produto anterior

O tradicional passou a dizer, em um caso da primeira pergunta, que o difusor que veio com o secador quebrou, mas o produto adquirido funciona bem. Antes, apresentava apenas a quebra do acessório antigo como achado, sem distinção suficiente. A melhora é pontual e não se repetiu em todas as fontes.

Na segunda pergunta, a fonte sobre substituir o difusor original que estava caindo continuou sendo resumida como se o produto atual tivesse começado a cair e precisado de substituição. Isso ocorreu nos dois métodos. O campo produto_atual reforçou a interpretação errada em vez de detectá-la. A ausência de contraponto de um verificador independente é uma limitação relevante.

### Condições de uso e estados físicos

Os dois métodos continuaram traduzindo “quando dobrado/colapsado fica pequeno” como “fica pequeno quando desdobrado”. O prompt explicava a distinção, mas ela não foi respeitada. A suposta causalidade entre tamanho compacto e amassamento foi retirada do relato principal; em seu lugar, o colapso relatado passou ao campo de suspeita, embora a pessoa o descreva como experiência, não como hipótese. Portanto, o erro de polaridade e a confusão entre fato relatado e suspeita não estão resolvidos.

Em outra fonte, a condição de mover o difusor durante o uso foi transformada em suspeita relacionada a movimento da cabeça. Essa troca do agente/objeto da ação não é sustentada pela avaliação. Também continuou aparecendo uma explicação causal sobre formato do difusor que a fonte não estabelece como causa comprovada.

### Suspeitas e propostas

No relato sobre a cabeça que se soltou do corpo, os dois métodos adicionaram suspeitas de falha de fabricação ou uso excessivo, ausentes naquela avaliação. O fato de o campo ser apresentado como “suspeita relatada, não comprovada” não autoriza atribuir ao consumidor uma hipótese que ele não formulou. Esse foi um problema importante desta rodada.

No caso de peças aparentemente coladas, a informação ficou no campo de suspeita/validação, mas o texto ainda poderia preservar melhor a ressalva do consumidor sobre a colagem. A separação de campos não garante que a modalidade correta seja preservada.

Continuam sugestões no campo de melhoria que são apenas verificações ou preservação de elogios, sem uma mudança de produto ligada a um problema. A tarefa de preservar qualidades é pertinente, mas não deveria ser apresentada indistintamente como correção de defeito. Algumas fontes com problemas explícitos foram resumidas principalmente pelos elogios.

## Entre os dois RAGs

As seis fontes comuns da primeira pergunta tiveram saídas individuais idênticas. Na segunda, os métodos tinham as mesmas oito fontes e produziram as mesmas oito análises individuais, com ordem diferente. A seleção temática ainda pode mudar as fontes da primeira pergunta; isso não tornou a interpretação das fontes comuns mais correta. Não há vencedor demonstrado.

## Decisão de desenvolvimento

A mudança de comprimento melhorou a legibilidade observada sem corte por caracteres ou tokens nesta rodada. A intervenção de prompt/rótulo não atingiu o objetivo principal de distinguir produtos e preservar condições de maneira confiável. Não se deve apresentar esta rodada como solução do problema de fidelidade.

Os exemplos atuais já foram usados repetidamente para orientar ajustes. São desenvolvimento e não teste independente; melhora pontual não garante generalização. Não será feita promoção automática à interface ou ampliação de produtos nesta entrega. Novas mudanças precisam de nova configuração/destino e avaliação de apoio semântico, sem ocultar as falhas desta rodada.

## Preservação, testes e reprodução

As quatro rodadas anteriores e artefatos experimentais registrados antes da execução foram conferidos por hash. Dados, fontes, saídas brutas e anotações individuais permanecem privados. Os relatórios públicos contêm agregados e discussão das limitações, sem corpus ou textos individuais.

Passaram 85 testes antes da geração. Eles incluem a aceitação de frases acima de 160 caracteres sem recorte, o teto agregado de tokens e a rejeição de propostas quando o referente é declarado não identificado. Não são avaliação independente dos rótulos ou das interpretações.

Configuração: configs/curly-product-pilot.v5-attribution.json. Executor: scripts/run_product_attribution_pilot.py. Resultados: results/product-pilot/curly-v5-attribution/.

```sh
.venv/bin/python scripts/report_product_attribution_pilot.py --output results/product-pilot/curly-v5-attribution/novos-agregados.json
```

O exportador e o executor recusam destinos existentes. Os agregados foram reproduzidos com igualdade byte a byte, sem novas chamadas ao modelo. Respostas e fontes completas estão no arquivo local de revisão, separado do Git.
