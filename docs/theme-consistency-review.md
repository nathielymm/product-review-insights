# Revisão de temas e consistência dos três conjuntos — 8 de novembro de 2026

Atualização da revisão com a usuária: houve concordância com as interpretações de cinco exemplos apresentados em conversa. As [decisões dessa rodada](theme-review-decisions.md) e o progresso em theme-review-progress.json são separados da auditoria inicial abaixo; não representam validação dos 90 comentários ou fechamento do recorte.

## Resultado principal

Os três candidatos continuam plausíveis como estudos de caso de heterogeneidade funcional. O conjunto compacto mantém uma classe de produto; o intermediário compartilha a rotina capilar; o variado reúne funções de áreas diferentes. A revisão não fecha o recorte.

A leitura de 90 comentários completos, seis de cada um dos 15 grupos parent_asin, encontrou os mesmos dez temas amplos propostos nos três conjuntos. A diferença está nas facetas concretas, nos produtos e nos contextos associados a esses temas. Isso não sustenta rotular os conjuntos como níveis comprovadamente crescentes de quantidade de temas de melhoria. Também não prova que tenham diversidade temática idêntica: o resultado depende da amostra e da granularidade da codificação.

Há compatibilidade geral com as classes de produto, mas versões, kits e identidade histórica exigem tratamento. Três parent_asin reúnem múltiplos ASINs de item. Não devemos atribuir a todos os comentários a versão e as promessas do título representativo do catálogo.

## Como a revisão foi feita

- Quinze grupos de produto, cinco por condição, sem IDs parent compartilhados entre os conjuntos escolhidos.
- Seis comentários por grupo: até dois com notas 1–2, dois com nota 3 e dois com notas 4–5; faltas preenchidas deterministicamente sem repetir comentário.
- Seed 101, independente das sementes da exploração semântica anterior.
- Mesmo universo já filtrado por inglês automático e 20–200 palavras. Na leitura desta amostra, os textos estavam em inglês; isso não certifica todo o corpus.
- Leitura integral e codificação qualitativa pelo assistente; não foi usado o Gemma nem o agrupamento do RAG para atribuir os temas.
- A codificação é uma proposta do assistente e ainda não foi validada pela usuária ou por revisora humana independente. Não é uma referência gold, avaliação humana concluída ou resultado de qualidade do RAG.

A amostra foi deliberadamente equilibrada por faixa de nota para diagnosticar problemas. No conjunto de esmaltes, não havia avaliações elegíveis de nota 3; foram usados três comentários de nota 1 e três de nota 5. Contagens abaixo descrevem apenas esta amostra, sem estimar prevalência dos temas ou taxas de inconsistência na população.

## Temas observados

| Conjunto | Facetas encontradas na leitura |
|---|---|
| Compacto | Aplicador grande, aplicação em camadas, grumos, volume/alongamento percebidos, transferência e descamação, remoção, conforto individual, preço e intenção de recompra. |
| Intermediário | Cheiro e textura, maciez/ressecamento percebidos, adequação ao cabelo, desembaraço, cerdas/estática, peso/botões/ruído/temperatura do secador, vida útil e garantia. |
| Variado | Fragrância e bomba do shampoo, aparência/aderência dos cílios, cores e cobertura dos esmaltes, quebra de frascos na entrega, encaixe/colapso/portabilidade do difusor, pilhas, entrada de água e vibração da escova dental. |

Esses são resumos das experiências relatadas, sem confirmação técnica de defeitos, mecanismos ou causas clínicas. Comparações pessoais de marcas ou resultados não provam superioridade, segurança nem composição do produto.

### Uma classificação ampla comum aos três

A matriz mostra quantos dos cinco grupos de produto tiveram pelo menos um comentário codificado em cada tema na amostra. Não representa a proporção de consumidores que pensam assim, e uma menção pode ser elogio, reclamação ou descrição de contexto.

| Tema amplo proposto | Compacto | Intermediário | Variado |
|---|---:|---:|---:|
| Desempenho e resultado percebido | 5/5 | 5/5 | 5/5 |
| Uso, aplicação, remoção e encaixe | 5/5 | 3/5 | 5/5 |
| Duração, estabilidade e confiabilidade | 5/5 | 2/5 | 4/5 |
| Embalagem, integridade e entrega | 1/5 | 1/5 | 2/5 |
| Características sensoriais e aparência | 4/5 | 5/5 | 5/5 |
| Conforto ou desconforto relatado | 5/5 | 4/5 | 3/5 |
| Informação e expectativas explícitas | 3/5 | 5/5 | 5/5 |
| Preço, quantidade e custo de uso | 4/5 | 5/5 | 4/5 |
| Contexto, preferências e adequação pessoal | 5/5 | 4/5 | 5/5 |
| Continuidade da compra e atendimento | 4/5 | 4/5 | 3/5 |

Todos os conjuntos alcançam dez temas nesse nível de resolução. Por exemplo, duração inclui fixação de maquiagem, estabilidade do acessório e vida útil de aparelho — aspectos diferentes sob uma categoria ampla. Uma referência de avaliação deve conservar essas facetas e o produto de origem, em vez de pontuar apenas a presença da palavra duração.

Essa leitura complementa a exploração por embeddings: comentários podem ficar mais distantes por falar de produtos diferentes, mesmo compartilhando necessidades amplas como uso, desempenho e valor. Precisamos manter separadas heterogeneidade de produtos/assuntos e diversidade temática anotada.

## Consistência entre catálogo e comentários

As categorias abaixo são julgamentos iniciais da leitura, não verificações de autenticidade. Compatível significa compatibilidade com a classe funcional; não certifica SKU, versão ou formulação.

| Conjunto | Comentários lidos | Compatíveis com a classe | Genéricos demais para confirmar isoladamente | Versão/oferta/aparência ambígua |
|---|---:|---:|---:|---:|
| Compacto — máscaras para cílios | 30 | 27 | 1 | 2 |
| Intermediário — rotina capilar | 30 | 26 | 4 | 0 |
| Variado — áreas diferentes | 30 | 28 | 0 | 2 |

Não identifiquei descrição inequivocamente de outra classe de produto nesta amostra. Os textos genéricos e ambíguos foram mantidos e sinalizados. Isso não garante consistência de todos os 3.936 comentários elegíveis disponíveis nos três candidatos, nem autoriza excluir comentários apenas por divergirem do catálogo.

### Parent ASIN não é garantia de uma versão única

Nas avaliações brutas válidas desses 15 grupos há 19 ASINs de item distintos. A maior parte dos grupos tem um item; os casos abaixo têm mais de um:

| parent_asin | ASINs de item distintos nas avaliações válidas | Consequência para o estudo |
|---|---:|---|
| B0B7L451Z9 | 2 | Não atribuir a versão waterproof do título a todos os relatos sem mapear o item. |
| B0BC3MQD29 | 3 | Há relatos de kit/tamanho/versão recebida diferente; o título representa uma oferta específica. |
| B01DD1NOZU | 2 | A função condicionador é compatível; confirmar modo leave-in versus uso no banho e versões. |

Os dois comentários de versão/oferta ambígua no compacto pertencem a B0BC3MQD29 e ao mesmo ASIN de item B01J4KYUJI. Eles falam de tamanho/kit e versão recebida diferentes do esperado. Isso reforça a necessidade de trabalhar com linhagem de item/oferta; não demonstra erro de classe nem defeito da fórmula.

No shampoo B012Q9NGE4, uma comparação entre compras menciona mudança de rótulo, foto e textura, apesar de haver um único ASIN de item nos registros. Um ID único também não garante versão histórica estável. No difusor, um relato menciona diferença de cor da peça em relação à imagem; essa alegação foi marcada, sem concluir que se trata de falsificação ou defeito confirmado.

### Recomendação de unidade de análise

Para este TCC, proponho tratar os grupos como famílias/classes funcionais de produto, mantendo parent_asin, ASIN de item e contexto/tempo como metadados. Quando não for possível mapear uma versão, usar rótulo neutro — por exemplo, linha de máscara para cílios — e restringir a análise ao que o comentário declara.

Assim, um relato só pode ser atribuído à versão waterproof quando essa identificação estiver sustentada. O mesmo cuidado vale para leave-in, kit de viagem, tamanho e composição. A alternativa é estudar SKUs/versões exatos, mas isso exige metadados históricos adicionais e pode reduzir bastante o volume.

Essa recomendação ainda precisa de alinhamento. O pipeline atual preserva parent_asin no corpus principal, mas não toda a linhagem de item; ela foi recuperada neste extrator de auditoria. Implementar a preservação de ASIN de item e a política de versões antes de montar corpora/índices finais.

## Fonte, logística e sugestões de melhoria

### Produto versus oferta e entrega

Os esmaltes têm relatos de frascos quebrados e vazamento na entrega; a máscara para cílios tem relatos de versão/kit recebido diferente. Isso sustenta investigar acondicionamento, informação da oferta ou execução da entrega. Não permite concluir automaticamente que a formulação é ruim ou que o fabricante foi responsável pela falha.

Precisamos distinguir nas respostas: problema do produto, embalagem/proteção, anúncio/versão, logística/vendedor e contexto de uso. Essa separação é importante para avaliar oportunidades de melhoria coerentes com as evidências.

### Pedidos explícitos são diferentes de propostas do analista

| Conjunto | Trechos com sugestão/desejo explícito de característica do produto/embalagem | Trechos com solicitação comercial/atendimento |
|---|---:|---:|
| Compacto — máscaras para cílios | 1 | 1 |
| Intermediário — rotina capilar | 2 | 1 |
| Variado — áreas diferentes | 2 | 0 |

Exemplos resumidos de desejos explícitos: consistência mais líquida, cerdas mais longas, embalagem alternativa, ajuste de intensidade da fragrância e maior variedade de cores. Um desejo por outra configuração não equivale necessariamente a um pedido formal ao fabricante.

A maioria dos relatos descreve experiências, não solicita mudanças diretamente. A pergunta de sugestões explícitas deve aceitar ausência de pedido no contexto recuperado. Propostas inferidas a partir dos problemas precisam ser apresentadas como hipóteses, sem inventar que consumidores as pediram ou que resolveriam o problema.

### Credibilidade e alegações a qualificar

- Um comentário do intermediário declara amostra gratuita; outro menciona apenas ter experimentado uma amostra, sem dizer que era gratuita.
- No variado, um comentário declara produto gratuito para dar opinião, e outro diz que recebeu gratuitamente sem esclarecer o contexto.
- Um comentário sobre cílios magnéticos alega recompensa por avaliação positiva. É uma alegação do autor, não confirmação de manipulação nem prova de que outras avaliações sejam falsas.
- Há relatos de desconforto e alegações sobre queda/crescimento de cabelo, ingredientes, toxicidade e ausência de cáries. Devem permanecer como relatos/opiniões atribuídos, sem estabelecer causalidade, eficácia clínica ou segurança.

Não removi automaticamente nenhum desses comentários. Recomendo marcadores de transparência e uma análise de sensibilidade pré-definida para divulgações de gratuidade/incentivos, separada do resultado principal. Não excluir amostras apenas por elogiar ou criticar.

## Consequências para as perguntas e o protocolo

1. Usar os mesmos temas amplos entre os conjuntos, mas registrar facetas específicas e o produto de origem. Não definir referências a partir dos clusters do método temático.
2. Há material para perguntas sobre uso, desempenho, valor, preferências e oportunidades inferidas. Perguntas de embalagem e pedidos explícitos têm evidência mais localizada; não exigir que todo conjunto apresente o mesmo tipo de problema.
3. Para comparar promessa e experiência, usar expectativas explicitamente descritas nos comentários ou uma oferta histórica corretamente vinculada. Não aplicar o título atual do parent a todas as versões.
4. Distinguir propostas de produto de problemas de entrega e atendimento. Separar pedidos explícitos, inferências do sistema e informações ainda ausentes.
5. Manter perguntas de limites (vendas/segurança) em avaliação separada de cobertura temática. Relatos individuais não sustentam previsão de vendas ou garantia de segurança.
6. As denominações compacto, intermediário e variado devem se referir por enquanto à heterogeneidade funcional/de assunto, não a uma quantidade comprovadamente crescente de temas.

Não alterei as 16 perguntas nem os índices nesta etapa. Essas observações servem para a próxima revisão e para fechar critérios de referência/aplicabilidade antes da avaliação.

## Parecer antes de fechar o recorte

Manter os três candidatos em revisão. Eles oferecem situações de uso e problemas interessantes e, nesta amostra, são em geral coerentes com as classes funcionais. Eu ainda não fecharia o recorte como 15 modelos/versões exatos nem como três níveis comprovados de diversidade temática.

As decisões pendentes são: adotar família funcional ou SKU/versão como unidade; validar a classificação temática com a usuária; vincular versões onde possível; separar logística e produto; e definir como tratar transparência de incentivos. Depois disso, revisar uma amostra adicional independente e congelar os critérios, antes de avaliar os RAGs.

## Arquivos e reprodução

```sh
.venv/bin/python scripts/prepare_theme_review.py
# Revisar sample.private.json e products.private.json localmente.
# Registrar a codificação proposta em assistant-coding.private.json, com hashes correspondentes.
.venv/bin/python scripts/summarize_theme_review.py
.venv/bin/python -m pytest -q
```

A seleção usa hashes determinísticos e pode ser reproduzida a partir dos dados e pools locais. As etiquetas foram propostas pelo assistente nesta conversa; o script apenas valida e agrega, sem chamar o Gemma nem gerar rótulos. Essa interpretação pelo assistente não equivale a revisão humana. Reproduzir exatamente as estatísticas de codificação requer o arquivo privado e o mesmo snapshot; outro revisor pode discordar e deve registrar a própria codificação. O código não inventa rótulos ausentes.

O codebook proposto está em configs/theme-review-codebook.draft.json. O resumo agregado está em docs/theme-consistency-summary.json. Comentários, linhagem detalhada e anotações por comentário permanecem em results/theme-review, fora do Git. Hashes verificam a correspondência entre amostra, codebook e codificação.

Passaram 25 testes, incluindo falta de notas intermediárias sem repetir comentários, rejeição de identidades duplicadas, correspondência das anotações com as fontes e invalidação quando a amostra muda. Nenhuma anotação humana independente foi declarada, nenhum corpus foi limpo automaticamente e nenhum resultado de desempenho do RAG foi calculado.
