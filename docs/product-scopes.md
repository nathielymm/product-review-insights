# Revisão das perguntas e proposta de recortes

Atualização de 8 de novembro de 2026: a proposta de dois produtos abaixo é histórica e não foi aprovada como recorte final. A investigação atual compara vários produtos de uma mesma categoria; consultar [o mapeamento de categorias](category-map.md) e configs/category-cohorts.draft.json. Os metadados oficiais já foram obtidos, mas não fornecem subcategorias preenchidas.

## Situação

Rascunho v2: 16 perguntas, substituindo a proposta de 30 perguntas discutida com a usuária. Prioridade: oportunidades de melhoria nos produtos, com apoio à análise de percepções e comunicação. Não foram executadas respostas finais nem escolhidos recortes com base no desempenho dos métodos.

Os campos question_pt e task facilitam a revisão; o runner usa question (inglês). scope_required registra uma exigência metodológica, ainda não implementada como filtro no runner. Nenhum recorte desta proposta foi aplicado ao índice existente.

## Perguntas revisadas

| ID | Pergunta para revisão |
|---|---|
| E01 | Quais dificuldades os consumidores descrevem na aplicação, remoção ou rotina de uso, excluindo problemas da embalagem? |
| E02 | Quais problemas da embalagem prejudicam proteção, conservação, abertura, fechamento ou dosagem? |
| E03 | Quais características sensoriais geram experiências negativas, e como são descritas? |
| E04 | Quais limitações de desempenho ou duração são relatadas, considerando o tipo de produto e as condições de uso mencionadas? |
| E05 | Quais diferenças aparecem entre a descrição ou promessa e a experiência recebida? |
| E06 | Quais características são valorizadas e quais motivos explícitos levam à recompra? |
| E07 | Quais aspectos sustentam percepções positivas e negativas de custo-benefício? |
| E08 | Quais motivos explícitos levam a interromper o uso ou não comprar novamente? |
| E09 | Quais mudanças no produto ou na embalagem são explicitamente solicitadas? |
| E10 | Que mudanças físicas ou funcionais podem ser propostas a partir dos problemas relatados, separando problema, proposta e o que permanece sem verificação? |
| E11 | Que melhorias nas instruções, informações ou comunicação poderiam tratar dúvidas e expectativas não atendidas? |
| E12 | Quais características valorizadas poderiam ser prejudicadas por mudanças voltadas às reclamações relatadas? |
| E13 | Quais características recebem elogios e críticas, e quais diferenças de preferência ou contexto são explicitamente mencionadas? |
| E14 | Quais limitações das avaliações impedem avaliar a viabilidade e o impacto de possíveis melhorias no produto? |
| E15 | As avaliações permitem determinar qual mudança aumentaria as vendas? Explique os limites das evidências. |
| E16 | As avaliações permitem garantir segurança para todos os consumidores? Explique os limites das evidências. |

Todas exigem evidências para afirmações sobre consumidores e reconhecimento explícito de aspectos não sustentados. Não ordenar oportunidades por frequência, impacto ou retorno financeiro a partir de poucos trechos recuperados.

Foram unidos: abertura/fechamento/dosagem, desempenho/duração, características valorizadas/motivos de recompra, pedidos explícitos de mudança no produto/embalagem, propostas de melhoria física/funcional, instruções/comunicação e conflitos de preferência/contexto. O mapa completo das junções está em configs/question-revision-map.json.

Diagnóstico e proposta permanecem separados porque avaliam capacidades diferentes. E09 verifica o que consumidores efetivamente pediram; E10 verifica se o sistema propõe mudanças justificadas sem apresentá-las como fatos. E11 trata mudanças de informação e comunicação, separadas das mudanças físicas/funcionais de E10. Perguntas relacionadas não devem ser interpretadas como temas estatisticamente independentes.

## Exploração dos dados

Fonte: mesmo Parquet fornecido, SHA-256 b40ae565f1073e0b4960e2f424fe0c82f3d270b7c4d00bc9272ddd6a8b7411d7.

Há 112.496 parent_asin com avaliações válidas e únicas. Desses, 725 têm pelo menos 100 avaliações e 38 têm pelo menos 500. A contagem usa as mesmas regras de texto válido, normalização, redação e deduplicação da ingestão. Isso é diferente da contagem bruta de 112.565 produtos.

Foram perfilados automaticamente os 40 produtos com maior volume válido. Para cada um, o script preparou até oito exemplos por nota, escolhidos por hash, e termos TF-IDF desse conjunto. A inspeção manual inicial examinou seis trechos (dois com nota 1, dois com nota 3 e dois com nota 5) de cada candidato da tabela abaixo, além dos termos. Essa inspeção é preliminar, não valida integralmente o catálogo nem estima prevalência de temas.

O arquivo contém avaliações e IDs de produto, mas não títulos oficiais/categorias do catálogo. Os tipos abaixo são inferidos dos relatos e precisam de confirmação com metadados oficiais antes da definição final. Nota baixa não equivale automaticamente a sentimento negativo: pode avaliar entrega, descrição ou outro aspecto.

| Tipo inferido | parent_asin | Válidas e únicas | Notas 1–2 | Nota 3 | Notas 4–5 | Textos com ≥20 palavras | No piloto global |
|---|---|---:|---:|---:|---:|---:|---:|
| Shampoo / cuidado capilar | B012Q9NGE4 | 838 | 148 | 73 | 617 | 529 | 18 |
| Difusor dobrável para secador | B019GBG0IE | 1.313 | 392 | 170 | 751 | 813 | 14 |
| Borrifador de névoa | B07C533XCW | 1.461 | 152 | 62 | 1.247 | 647 | 18 |
| Máscara / condicionador capilar | B0BV1FPZY6 | 598 | 32 | 21 | 545 | 364 | 6 |
| Tintura usada nas sobrancelhas, segundo relatos | B0BM4GX6TT | 1.694 | 265 | 141 | 1.288 | 1.058 | 21 |

Contagens anteriores a qualquer filtro de idioma. Foram encontrados exemplos em espanhol entre os candidatos: validar idioma antes do experimento em inglês. Textos longos são apenas uma aproximação da riqueza descritiva, não garantia de qualidade.

## Proposta

Começar com dois estudos de caso separados dentro de cuidados capilares:

1. Shampoo, B012Q9NGE4. Nos exemplos, há experiências sobre cheiro, espuma, resultado percebido no cabelo, ressecamento, embalagem e expectativas. Permite investigar melhorias na experiência e informação do produto, sem transformar relatos em conclusões clínicas.
2. Difusor, B019GBG0IE. Nos exemplos, aparecem encaixe no secador, colapso durante o uso, material, portabilidade e resultado percebido. Há volume de notas baixas, intermediárias e altas suficiente para investigar experiências divergentes. É um caso complementar de acessório físico, em vez de formulação cosmética.

Reservar o borrifador B07C533XCW como candidato a desenvolvimento separado dos casos finais: exemplos abordam mecanismo, névoa, tamanho, facilidade de abertura e durabilidade. Há usos capilares e outros usos; declarar esse contexto caso ele seja selecionado. É também alternativa de avaliação, se a usuária preferir substituí-lo pelo difusor, mas não deve servir ao desenvolvimento e ao teste final simultaneamente.

A máscara é alternativa coerente para um estudo só de cosméticos capilares, mas apenas 32 das 598 avaliações válidas têm notas 1–2. Isso não a invalida; reduz o material potencial para estudar certos problemas. A tintura tem volume, mas os relatos levantam divergências sobre o uso indicado e instruções. Confirmar o catálogo e a finalidade antes de incluí-la; não recomendar mudanças de formulação ou uso a partir desses relatos.

Nem todos os produtos mais volumosos são adequados: a inspeção de B0BTLTVR1X encontrou relatos aparentemente de itens muito diferentes (por exemplo, acessórios e repelência de animais). Não usá-lo sem investigar a consistência da identidade do produto. ASIN pode agrupar variantes, mudanças históricas ou registros heterogêneos; mesmo um recorte por ID precisa de revisão.

## Amostragem e próximos passos

Não filtrar apenas a amostra global de 10 mil: ela contém somente 18 avaliações do shampoo e 14 do difusor. Os respectivos recortes devem ser extraídos do Parquet completo. Os 838 e 1.313 registros são candidatos a corpus por produto, antes de filtro de idioma e revisão de consistência. Manter a distribuição natural de notas; não escolher avaliações negativas em excesso para produzir mais oportunidades. A amostra equilibrada por nota do perfil serve exclusivamente à inspeção qualitativa.

Se forem usados dois recortes e todas as 16 perguntas, teremos 32 casos pergunta × produto. Dois métodos e três repetições produzem 192 respostas, das quais 24 correspondem às perguntas de limites (E15–E16). Isso não equivale a 192 perguntas independentes. Ajustar o esforço de anotação antes de congelar o protocolo. Para resultados por recorte, o bootstrap atual opera por pergunta; ao reunir recortes, não tratar o mesmo texto de pergunta em produtos diferentes como independente sem declarar a estrutura e ajustar a análise.

Antes de executar: confirmar catálogo/consistência; validar idioma e dados pessoais residuais; escolher os produtos; extrair corpora por produto; implementar e verificar restrição de escopo; adaptar e congelar perguntas aplicáveis; construir referência independente dos clusters. Não há conclusão de superioridade dos métodos nesta exploração.
