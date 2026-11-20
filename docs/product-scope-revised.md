# Produtos e critério de identidade revisados

Estado: critério metodológico corrigido conforme alinhamento com a usuária; candidatos revisados, sem seleção final de quantidade, novos agrupamentos ou geração de avaliação. Esta revisão substitui as recomendações restritivas sobre homogeneidade de versão da auditoria anterior. Suas contagens e evidências de identidade permanecem válidas.

## Critério adotado

Uma análise trata de um produto identificável, podendo incluir sua história, versões, tamanhos ou componentes quando a unidade é um kit. Mudanças de fórmula, aplicador, embalagem ou desempenho relatadas não são motivo de exclusão: podem ser achados importantes para oportunidades de melhoria.

A identidade do produto é operacional e explícita, apoiada em códigos, função, metadados locais e relatos. parent_asin sozinho não é prova de equivalência funcional, e asin sozinho não certifica estabilidade de versão. Um produto pode ter vários códigos de item; não se exige um estudo separado para cada um. Não juntar shampoo, condicionador, outros modelos ou marcas apenas por pertencimento à mesma linha ou categoria. Produtos diferentes usados em conjunto podem ser mencionados como contexto, sem atribuir ao produto-alvo seus efeitos isolados.

A referência e a resposta devem preservar quem experimentou o quê, compras anteriores/atuais e variantes quando identificadas. Quando a versão não é informada, registrar essa lacuna, sem inventar uma classificação. Datas e opiniões divergentes não comprovam mudanças de fórmula. Não concluir que uma reformulação causou um problema nem atribuir à versão atual todos os relatos históricos.

## Revisão dos candidatos

As contagens usam as avaliações elegíveis já preparadas. Não são estimativas de mercado, quantidade mínima universal ou referência exaustiva. Não é obrigatório usar todos os candidatos no estudo final.

| Produto/caso proposto | Avaliações | Identificação e tratamento |
|---|---:|---|
| Difusor dobrável The Curly Co. | 804 | Um produto; preservar encaixe em secadores diferentes e comparações com outros difusores. |
| Escova GranNaturals | 613 | Manter diferenças relatadas de cerdas e compras anteriores; não excluir por possível mudança. |
| Shampoo Pure Body Naturals Argan | 473 | Reintegrado: relatos de reformulação, tamanho e embalagem são parte da análise. |
| Escova dental Sonicare HX3351 | 397 | Analisar este modelo; distinguir experiências com outros modelos citados nas comparações. |
| Máscara capilar Sauce Guacamole | 352 | O item observado é B07K7VD98J; preservar diferenças de amostra/sachê e embalagem maior. |
| Leave-in Carol’s Daughter Almond Milk | 174 | Caso restrito a B01DD1NOZU por enquanto; não juntar automaticamente o segundo item de função incerta. |
| Máscara Essence I Love Extreme | 145 | Caso da linha representada por dois itens: 141 + 4; manter os códigos e não adivinhar versões por filho. |
| Kit de cílios magnéticos Veshely | 128 | Produto-kit; atribuir problemas aos componentes ou estilos quando o relato permitir. |
| Máscara Bold Lash | 123 | Reintegrada: mudança relatada de fórmula/aplicador é aspecto de interesse, não exclusão. |
| Máscara Essence Lash Princess | 119 | Reintegrada como linha representada nos dados; preservar regular/waterproof e coleção quando mencionadas, sem assumir mesma versão. |
| Secador Warmlife | 104 | Especificações conflitantes do catálogo são incerteza de atributo, não motivo suficiente para excluir o produto. |
| Shampoo Okay Castor | 103 | Reintegrado; suspeitas de mudança/diluição permanecem relatos, sem confirmação de causa. |
| Máscara Too Faced Better Than Sex | 91 | Caso com três itens: 87 + 2 + 2; diferenciar tamanho e waterproof/regular quando explícitos. |
| Conjunto Cosmetic Art 30 esmaltes | 89 | Elegível como produto-kit, não como um único esmalte ou acabamento. |
| Máscara Lash Ease Fiber | 69 | Candidato com menos avaliações; quantidade e disponibilidade de aspectos serão verificadas no piloto. |

Total dos candidatos: 3.784 avaliações em 15 casos de produto. Nenhum candidato foi retirado por mudança de fórmula. A lista estabelece elegibilidade para consideração, não garantia de profundidade ou obrigação de manter os 15.

## Dúvida de identidade que permanece

As outras 59 avaliações da família Carol’s Daughter correspondem ao item B01D6O4Y12. Há relatos de enxágue, condicionador e shampoo e comparações com leave-in; o catálogo disponível descreve a família, sem ficha específica desse filho. Isso não permite identificá-lo automaticamente como o mesmo leave-in nem provar que todos os relatos sejam de um condicionador com enxágue.

Esse item fica como candidato separado com identidade pendente, e não como exclusão por versão. Os registros foram preservados. Eles poderão entrar como outro produto se sua identidade for esclarecida. Não classificar cada avaliação como shampoo/condicionador só por uma palavra isolada.

## Efeito na preparação e na metodologia

configs/product-focused-scope.draft.json registra os 15 casos, os itens permitidos por caso, as contagens e a pendência. Os 19 rascunhos por item já preparados são blocos de rastreabilidade e podem ser combinados pelo mapeamento explícito do produto. Não definem obrigatoriamente 19 análises científicas distintas. Nenhum corpus anterior foi reescrito; a configuração ainda não está ativa no runner nem na interface.

A sequência passa a ser: delimitar produto → reunir suas avaliações e linhagem → construir temas dentro do produto → recuperar evidências para a pergunta → gerar achados atribuídos → avaliar fidelidade, cobertura e propostas. Os dois RAGs usarão o mesmo corpus por produto. O temático diversificará temas internos, sem misturar produtos para obter variedade.

A próxima preparação deve criar corpus e manifesto por caso conforme o mapeamento, inclusive as variantes permitidas, em destinos novos. Não se exige rotular todas as versões antes de começar; exige-se preservar distinções que as fontes oferecem e qualificar as desconhecidas. Escolha da quantidade de produtos, piloto, orçamento e avaliação permanecem para alinhamento e desenvolvimento, sem nova grande grade automática.
