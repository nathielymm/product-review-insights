# Perguntas específicas por produto — proposta para revisão

Estado: rascunho, sem congelamento, sem geração de respostas finais e sem referência aprovada. A seleção abaixo decorre de leitura dirigida por assunto e nota, não de anotação integral dos 1.209 comentários. Os três corpora têm 613, 473 e 123 avaliações elegíveis. Os dados já foram explorados e não são um teste intocado.

## Princípios

Cada pergunta analítica busca diagnóstico e oportunidades de investigação, sem exigir que a melhoria já esteja comprovada. O texto não fornece exemplos de respostas ou conclusões esperadas ao modelo. Os dois RAGs receberão a mesma pergunta e corpus por produto. A avaliação principal usa o inglês original; traduções e equivalentes de busca serão documentados antes do congelamento. Fontes individuais ficam somente no armazenamento local ignorado pelo Git.

Q1–Q4 investigam aspectos delimitados. Q5 avalia escolha justificada de oportunidades e trade-offs; Q6 avalia limites de previsão. Q5 será uma consulta independente às avaliações, sem encadear respostas anteriores. As oportunidades não devem ser apresentadas como causas ou soluções comprovadas.

## Questões por produto

### Escova GranNaturals

1. Que dificuldades para alcançar as camadas internas do cabelo são relatadas com esta escova? Que ajustes nas cerdas poderiam ser investigados, considerando os tipos de cabelo e as experiências favoráveis descritas?

2. Como os relatos sobre estática, volume e acabamento do cabelo divergem? Que melhorias poderiam ser investigadas preservando os benefícios de brilho e controle da oleosidade mencionados?

3. Que dificuldades de pegada são associadas ao tamanho, à largura e ao formato da escova? Que mudanças ergonômicas poderiam ser investigadas sem presumir que o mesmo tamanho seja inadequado para todas as pessoas?

4. Como o odor da escova afetou a experiência de uso e o que aconteceu nas tentativas de reduzi-lo? Que verificações ou melhorias seriam pertinentes, sem deduzir a composição química pelo cheiro?

### Shampoo Pure Body Naturals Argan

1. Em quais experiências o shampoo é descrito como limpando sem ressecar e em quais aparecem ressecamento ou oleosidade após a lavagem? Que melhorias de desempenho ou orientação de uso poderiam ser investigadas, considerando apenas as condições relatadas?

2. Que dificuldades são relatadas para retirar e dosar o shampoo, incluindo funcionamento da válvula e aproveitamento do conteúdo? Que melhorias na embalagem poderiam ser investigadas sem confundir preferência de dosagem com defeito confirmado?

3. Que diferenças entre compras são relatadas na consistência, quantidade e apresentação do shampoo? Que oportunidades existem para melhorar a consistência da entrega e a comunicação de mudanças, distinguindo observações de suspeitas de diluição ou reformulação?

4. Que aspectos da fragrância agradam e quais dificultam o uso? Que melhorias de produto ou de informação poderiam ser investigadas, preservando as preferências divergentes e sem inferir ingredientes ou segurança pelo cheiro?

### Máscara de cílios Bold Lash

1. Que dificuldades de aplicação são associadas ao tamanho, ao formato ou à mudança do aplicador? Que ajustes poderiam ser investigados, distinguindo o que é atribuído ao aplicador do que não pode ser separado da fórmula?

2. Em quais relatos o efeito de alongamento, volume ou definição atende às expectativas e em quais é comparado desfavoravelmente a máscaras mais baratas? Que melhorias de desempenho ou comunicação de valor poderiam ser investigadas?

3. Como os relatos sobre duração, manchas ou descamação e facilidade de remoção se contrastam? Que melhorias poderiam ser investigadas para equilibrar permanência e remoção, sem presumir que todas as pessoas usaram a mesma versão ou rotina?

4. Que problemas são relatados na condição da máscara ao abrir a embalagem e na sua conservação durante o uso? Que verificações ou melhorias poderiam ser investigadas, distinguindo unidades secas ou vazias, formação de grumos e falhas físicas, sem presumir uma causa comum?

## Perguntas comuns aplicadas separadamente aos três produtos

5. Considerando os aspectos analisados deste produto, selecione até duas oportunidades de melhoria para investigar primeiro. Justifique pela consequência relatada para o uso, pelo apoio das avaliações e pelas qualidades a preservar; indique o que precisaria ser testado, sem estimar retorno comercial.

6. Essas avaliações permitem afirmar qual das melhorias propostas aumentaria mais as vendas deste produto? Explique os limites da conclusão e que informações adicionais seriam necessárias, distinguindo hipóteses de previsões.

## Fronteiras para evitar repetição

- Escova: Q1 trata de alcance mecânico das cerdas; Q2, acabamento/estática; Q3, pegada; Q4, odor. Queda de cerdas não é uma tarefa separada nesta proposta, que não pretende cobrir todos os assuntos do corpus.
- Shampoo: Q1 trata da experiência de lavagem; Q2, retirada/dosagem; Q3, comparação explícita entre compras; Q4, fragrância. Um relato pode apoiar duas perguntas, mas as mesmas evidências não serão contadas duas vezes dentro do mesmo critério da mesma resposta. Vazamentos no transporte podem aparecer como contexto de embalagem, sem serem confundidos com falha da válvula durante uso.
- Máscara: Q1 trata da aplicação e atribuição ao aplicador; Q2, efeito visual e valor percebido; Q3, permanência/remoção; Q4, condição da unidade e conservação. Grumos na aplicação e conteúdo já seco ao abrir exigem atribuição distinta.
- Q5 mede seleção justificada, não uma nova lista completa de problemas. Não inferir prioridade de mercado, frequência populacional, viabilidade técnica ou aumento de vendas. Não comparar notas brutas de questões de dificuldade distinta como se fossem equivalentes.

## Escala ainda proposta

Mantêm-se 18 perguntas concretas (seis para cada produto), 36 respostas principais e 24 gerações adicionais somente para estabilidade de Q1/Q5. Todas as quantidades e repetições continuam propostas. Não houve alteração do gerador, da interface, dos experimentos ou da configuração congelada anterior. As referências e sua aplicabilidade precisam ser preparadas antes da avaliação final.
