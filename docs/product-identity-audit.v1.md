> Critério revisado: mudanças de fórmula ou versão não excluem produtos. As contagens desta auditoria foram preservadas; as decisões de espera por homogeneidade foram substituídas em [product-scope-revised.md](product-scope-revised.md).

# Auditoria de identidade para análise de um produto por vez

Estado: separação técnica em rascunho, com revisão de identidade ainda necessária. A busca deve usar um item por consulta e os temas devem ser construídos dentro dele. Não há confirmação de homogeneidade de versão, novos temas ou novos resultados de RAG nesta auditoria.

## O que foi conferido

Foram examinados os identificadores das 3.843 avaliações elegíveis das 15 famílias já selecionadas, seus códigos no Parquet de avaliações e os metadados locais correspondentes. A fonte de avaliações tem campos asin e parent_asin; o catálogo local tem parent_asin, título, detalhes e atributos da família, sem vínculo histórico de versão por avaliação. Não foi feita uma seleção entre todos os produtos do arquivo de 701.528 registros.

As 15 famílias correspondem a 19 itens distintos. Três famílias reúnem mais de um item: Essence I Love Extreme, Too Faced Better Than Sex e Carol’s Daughter Almond Milk. Nos corpora elegíveis atuais, cada avaliação tem linhagem para um único item; não houve linhagem múltipla a colocar em quarentena. Isso permite separação por código, mas não demonstra que o item manteve a mesma composição, aplicador ou embalagem no tempo.

O arquivo product-identity-audit.v1.json contém contagens agregadas, hashes e triagem lexical. Foram sinalizados 280 registros para possível atenção a versões, tamanhos ou comparações. As buscas por palavras têm falsos positivos e omissões: “minha escova antiga” pode ser outra marca, e “precisa de novo design” pode ser uma proposta. A ausência de marcação não prova identidade estável. Foram lidos os relatos sinalizados de mudança de fórmula/versão/aplicador e trechos adicionais de candidatos; não se alega revisão humana ou semântica exaustiva de todos os registros.

## Candidatos para revisão prioritária

Quantidades abaixo são avaliações elegíveis e deduplicadas já preparadas, não todas as ocorrências brutas nem contagens finais após nova revisão. Os nomes são descrições vinculadas à família nos metadados, sem certificação de cada versão histórica.

| Descrição | Item ASIN | Avaliações | Por que considerar / cuidado restante |
|---|---|---:|---|
| Difusor dobrável The Curly Co. | B019GBG0IE | 804 | Um código observado; relatos de encaixe, colapso e durabilidade. As comparações com outros difusores e sugestões de redesenho não provam mudança deste modelo. Conferir acessórios e medidas sem atribuir causas às diferenças de desempenho. |
| Máscara capilar Sauce Guacamole Whip | B07K7VD98J | 352 | Um item observado, diferente do código da família B0BV1FPZY6. Há relatos de amostras/sachês e embalagem maior; separar o que se refere à amostra, ao produto recebido e ao tamanho, principalmente para perguntas de embalagem. |
| Condicionador leave-in Carol’s Daughter Almond Milk | B01DD1NOZU | 174 | Pode ser isolado do outro item da família; há experiências de aplicação em cabelo seco/úmido. Conferir relatos sobre shampoo/condicionador usados em conjunto, sem transferir efeitos entre produtos. |
| Kit de cílios magnéticos Veshely | B08BZNW9NK | 128 | Um código observado; tratar o kit como produto, incluindo delineador/aplicador. Não tratar cada estilo de cílio como idêntico nem confundir experiência com extensão de cílios. |
| Máscara de cílios Lash Ease Fiber | B07M5HB65T | 69 | Um código observado e menos avaliações que os demais; candidato de máscara para revisar sem juntar outras marcas. Não há certificação de fórmula estável pela ausência de alerta lexical. |

Esses cinco são prioridades de verificação, não recorte final ou lista de produtos certificados sem mistura de versões. Não há limite de amostra ou quantidade de produtos automaticamente aprovada nesta entrega.

## Casos que exigem separação ou ficam em espera

| Família descritiva | Separação observada nas avaliações elegíveis | Decisão de identidade proposta |
|---|---|---|
| Carol’s Daughter Almond Milk | B01DD1NOZU: 174; B01D6O4Y12: 59 | Não juntar. O segundo item não tem metadado próprio no arquivo local consultado; seu tipo exato não pode ser herdado automaticamente do título de leave-in da família. |
| Essence I Love Extreme | B012XYSK1G: 141; B09V1C22T3: 4 | Separar códigos. Sem catálogo específico para cada filho, não rotular as duas variantes por fórmula/cor/resistência a água com base apenas no título da família. Quatro avaliações elegíveis oferecem pouco material para um caso aprofundado isolado. |
| Too Faced Better Than Sex | B01J4KYUJI: 87; B01HFMB6EE: 2; B078919VBD: 2 | Não juntar. Título da família menciona mini waterproof; relatos incluem comparações de fórmula original/waterproof e tamanhos. Não assumir o mesmo tamanho ou versão para todos os filhos. |
| Bold Lash | B01557EHW4: 123 | Mesmo código contém relatos explícitos de mudança de fórmula e formato de aplicador. Não tratar o conjunto como uma versão homogênea. Não há mapeamento que permita separar com segurança todas as avaliações por geração. |
| Shampoo Pure Body Naturals | B012Q9NGE4: 473 | Relatos explícitos de reformulação, embalagem e alteração de tamanho sob um código. Deixar em espera para análise de produto homogêneo. Datas não bastam para rotular automaticamente fórmula antiga/nova. |
| Essence Lash Princess / Disney Snow White | B08TCBP8HV: 119 | O catálogo descreve coleção Disney/Snow White, mas os relatos mencionam versões regular e waterproof, inclusive compras para pessoas diferentes. Um código único não autoriza afirmar mesma versão. Deixar em espera, inclusive o exemplo usado na interface. |
| Shampoo Okay Castor | B00DPNKDR4: 103 | Um item observado sob família B0CDNZ7F2V; relatos suspeitam de alteração de fórmula ou diluição pelo vendedor. Não comprovar causa ou reformulação, mas não presumir homogeneidade. |
| Escova GranNaturals | B00R1TAN7I: 613 | Relato compara compra anterior à nova, com diferença de rigidez das cerdas; outros comparam marcas diferentes. Um código não basta para decidir se há mudança real de versão. |
| Escova dental Sonicare HX3351 | B000FEIOHW: 397 | Muitas comparações com modelos recarregáveis anteriores e relato de alteração percebida de rigidez. Exige separação de experiências do modelo analisado e dos outros; não atribuir ao modelo a bateria ou falha de outro aparelho. |
| Secador Warmlife | B01M1IEADO: 104 | Metadados internos conflitam: título 1875 W/preto e detalhes 2000 W/prateado. Não certificar especificação ou versão única com esse catálogo. |
| Conjunto Cosmetic Art 30 esmaltes | B01LBESKBO: 89 | É um kit com múltiplas cores e acabamentos. Pode ser um produto-kit se essa for a unidade escolhida, mas não um esmalte/fórmula única. Não priorizar se o objetivo for um item materialmente homogêneo. |

Uma suspeita do consumidor não prova alteração industrial, falsificação ou culpa do vendedor. O objetivo desta triagem é evitar afirmar equivalência que os dados não sustentam, não eliminar reclamações inconvenientes. A contagem de candidatos pode cair após revisão ou permanecer ambígua.

## Reorganização local realizada

As 3.843 avaliações foram copiadas para 19 casos de item em data/processed/product-focused-draft/items/<asin>/, sem modificar os corpora anteriores. Cada registro usa o código do item como product_id e mantém o código da família em parent_product_id, além da linhagem e das datas originais. Os manifestos têm hashes, contagens e marcação explícita version_purity_confirmed=false e topics_rebuilt=false. Nenhum item em espera foi aprovado automaticamente porque possui uma pasta.

A separação usa o conjunto elegível existente, não adiciona avaliações brutas ou altera os critérios de limpeza/língua. Novos corpus/manifestos têm esquema de rascunho separado e não devem ser apresentados como os índices congelados antigos. Os novos agrupamentos deverão ser construídos por item após delimitar o recorte; o filtro atual da interface ainda não certifica versões nem usa esses novos casos.

## Próximo passo para fechar produtos

Revisar prioritariamente os cinco candidatos, com foco em identidade, usos de amostra/kit, experiências sobre outro produto e atributos conflitantes, preservando tanto elogios quanto reclamações. Registrar decisões por evidência em arquivos privados. Não inferir versões apenas por desempenho distinto, sentimento, palavras-chave ou um corte temporal arbitrário. Quando não houver identificação suficiente, manter o relato com qualificação para tarefas compatíveis ou excluir o candidato do estudo homogêneo por regra documentada; não inventar rótulos de versão.

Somente depois definir quantos produtos compõem o estudo e construir temas, perguntas e referências dentro de cada item. A nova avaliação não deve alegar que os 15 casos precisam ser mantidos nem que o número de avaliações determina sozinho a qualidade. O critério de identidade vem antes do desempenho do RAG.

## Reprodução

A auditoria exige os arquivos privados locais. Usar destinos novos:

```sh
.venv/bin/python scripts/audit_product_identity.py --output results/product-identity-audit/nova-auditoria.json --private-output results/product-identity-audit/nova-triagem.private.json
.venv/bin/python scripts/prepare_product_cases.py --output data/processed/product-focused-novo-rascunho
```

A triagem privada contém textos e não deve ser versionada. O relatório público tem somente agregados; o código não distribui os dados.
