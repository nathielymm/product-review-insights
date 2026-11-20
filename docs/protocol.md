# Protocolo experimental — versão de desenvolvimento

## Hipótese e comparação

O agrupamento pode aumentar a diversidade das evidências e a cobertura dos insights, com possível perda de relevância ou aumento do custo. A hipótese não pressupõe ganho. Comparação pareada no mesmo corpus, perguntas, encoder, FAISS, Gemma, prompt, número máximo de trechos e orçamento de contexto. O tamanho real do contexto e a quantidade de evidências podem diferir e devem ser reportados.

O enriquecimento consiste em diversidade por cluster nos top-80 candidatos, não em uma segunda fonte de conhecimento. Uma ablação futura poderá comparar com MMR; ela não integra o experimento principal atual. Os grupos devem ser inspecionados por termos e representantes; ajustar K apenas no desenvolvimento. Registrar coerência e estabilidade em mais de uma seed antes de congelar K.

## Dados e privacidade

Usar o Parquet fornecido, registrar SHA-256 e confirmar procedência antes da apresentação final. O esquema não traz categoria explícita. O dataset é publicamente disponibilizado pelo McAuley Lab, mas disponibilidade pública não equivale a autorização irrestrita para redistribuição. Registrar as condições da fonte antes de distribuir qualquer derivado. Não redistribuir corpus, trechos, respostas ou IDs de consumidores. O código remove user_id e imagens; redação heurística de texto requer revisão manual para nomes/endereço e outros identificadores residuais.

A amostra por hash é uniforme entre avaliações válidas e únicas; não estratificada. Reportar distribuição de notas e idioma. Não traduzir avaliações no experimento principal. Verificar idioma na amostra e definir regra de inclusão antes do teste. A preparação não utiliza perguntas nem rótulos de avaliação.

## Perguntas e referência

As 10 perguntas em questions.dev.json são exclusivamente de desenvolvimento. O rascunho v2 em questions.eval.draft.json contém 16 perguntas, com texto em inglês e tradução para revisão em português. Ele substitui a proposta de 30 perguntas discutida na conversa, juntando tópicos próximos e separando diagnóstico, sugestões explícitas, propostas inferidas e limites das conclusões. question-revision-map.json documenta as junções. Não é um benchmark validado nem congelado.

Todas as perguntas do rascunho v2 exigem um recorte explícito de produto. O campo scope_required documenta essa exigência, mas o runner atual ainda não impõe filtro por produto: não executar esse rascunho como teste final no índice global. Após a escolha dos recortes, preparar corpora/índices separados ou implementar filtros verificados. Não basta mencionar o produto no prompt. As evidências e os grupos devem pertencer ao mesmo recorte nos dois métodos.

Revisar a aplicabilidade das perguntas por produto antes do congelamento. Perguntas com aspectos sem suporte devem permitir abstenção; não excluir perguntas depois de observar qual método responde melhor. Para pontuar cobertura, o denominador é a referência específica de cada pergunta e produto. A proposta de recortes e as limitações estão em product-scopes.md. Congelar arquivo, recortes e hashes antes da primeira execução final e não otimizar parâmetros com seus resultados.

As 16 perguntas não representam 16 temas independentes: algumas avaliam tarefas distintas sobre evidências relacionadas (por exemplo, descrever um problema e propor uma melhoria). Reportar resultados por tarefa e recorte e reconhecer essa dependência. E15 e E16 são testes de limites, avaliados separadamente de cobertura temática. E12 e E14 incluem análise de trade-offs e lacunas; propostas hipotéticas corretamente identificadas não devem ser contadas como relatos de consumidores, e sua utilidade precisa de julgamento específico.

A exploração atual em category-map.md considera vários produtos da mesma categoria, sem fechar o recorte. Os metadados oficiais têm categories vazio em todos os registros; regras de título em category-rules.json são uma taxonomia provisória, não rótulos oficiais. Separar função/formato e famílias/variantes antes do congelamento. A triagem de ≥100 avaliações e ≥30 textos com ≥20 palavras por ID é operacional, não evidência de saturação temática ou independência estatística. Se houver amostragem por produto, definir o peso de cada produto e preservar a distribuição de notas; as contagens atuais antecedem filtro de idioma. Rever a unidade de reamostragem e a estrutura de dependência caso os mesmos produtos ou perguntas sejam reunidos na análise.

A etapa seguinte, documentada em diversity-candidates.md, explora três condições de heterogeneidade com cinco produtos cada. As configurações estão em diversity-candidates.draft.json e diversity-shortlist.draft.json. É uma exploração dos corpora antes de avaliar os RAGs; os indicadores semânticos não são cobertura/fidelidade de respostas nem uma referência temática. Foram examinados todos os candidatos declarados, incluindo os que levantam problemas de identidade do produto. A gradação de distância de cosseno é estável nas amostras, mas a ordenação de entropia de clusters depende de K. Não rotular as condições como níveis comprovados de diversidade temática.

As amostras exploratórias têm 30 comentários por produto, total de 150, com filtro automático de inglês e faixa de 20–200 palavras. Controles separados igualam faixas de comprimento (150 comentários) e proporções de notas (125 comentários, sem nota 3); estes últimos são sensibilidades e não amostras representativas da população. Os corpora finais ainda não foram definidos. A avaliação futura deve registrar a condição, produtos, amostra e perguntas aplicáveis, usar os mesmos limites nos dois métodos e respeitar sobreposição/reutilização de perguntas. Se houver um único conjunto por condição, não usar sementes de comentários ou repetições do LLM como réplicas independentes de heterogeneidade; limitar a conclusão aos estudos de caso.

A leitura de consistência em theme-consistency-review.md foi feita pelo assistente em 90 comentários selecionados com estratificação por nota; os rótulos ainda dependem de validação humana. Os mesmos dez temas amplos propostos aparecem nos três candidatos, com facetas específicas diferentes. Isso não valida uma escala ordinal de quantidade de temas. A taxonomia ampla é um rascunho em theme-review-codebook.draft.json, não a referência final de cobertura das respostas.

Preservar a ligação entre parent_asin e ASIN do item antes da ingestão final. O título representativo do parent não pode ser aplicado automaticamente a versões, kits e compras históricas diferentes. A unidade de análise (família funcional versus SKU/versão) permanece pendente. Separar problema de produto, anúncio/oferta, entrega, atendimento e contexto pessoal nas inferências de melhoria. Marcar gratuidade e alegações de incentivo sem assumir fraude; qualquer exclusão ou sensibilidade deve ter critérios definidos previamente e resultados transparentes. Sugestões explícitas, preferências por características e propostas inferidas não são equivalentes.

Para cada pergunta, anotar temas relevantes e IDs de suporte a partir de um conjunto de evidências revisado independentemente dos clusters. É viável começar com um pool de evidências obtido por múltiplas estratégias e busca manual; nesse caso, explicitar que a cobertura é relativa ao pool, não a todo o universo de avaliações. Evitar usar exclusivamente a união dos dois métodos, que pode ocultar temas não recuperados por ambos. A referência deve ser fechada antes de avaliar respostas.

Perguntas de abstenção não recebem cobertura temática quando não há temas de referência. Avaliar acerto de abstenção separadamente, manualmente. Questões de prevalência exigem dados agregados apropriados e não podem ser respondidas com frequência em trechos recuperados.

## Execução e recursos

Executar três repetições por pergunta/método. Alternar ordem dos métodos com seed fixa; registrar a ordem observada no JSONL. Fazer aquecimento separado e medir carregamento frio em experimento específico; não misturar latências frias e aquecidas. Temperatura zero e seed não garantem igualdade bit a bit em todas as plataformas.

Capturar tempo de recuperação (inclui embedding da pergunta), geração e total; tokens de entrada/saída, tempo de carregamento e geração fornecidos pelo Ollama; RSS amostrado do Python e processos Ollama acessíveis, CPU do processo Python e tamanho em disco. RSS não mede separadamente memória GPU/Metal e pode contar páginas compartilhadas. CPU Python não inclui CPU do servidor Ollama. Energia e custo monetário não serão estimados sem metodologia e medição próprias. Reportar preparação/indexação separadamente do custo por consulta.

## Anotação e métricas

Exportar respostas e evidências com IDs cegos. Guardar key.private.json separado da revisora. Não incluir método, cluster ou score no material de anotação. A ordem das evidências e o estilo da resposta ainda podem fornecer pistas; reconhecer essa limitação.

Para cada resposta, dividir o texto em afirmações factuais atômicas. Marcar cada uma como sustentada pelas citações, contradita ou sem suporte. Marcar temas de referência cobertos apenas se a afirmação correspondente estiver sustentada. Registrar notas com a justificativa. Duas revisoras, se viável, devem anotar uma parte em comum e discutir divergências; com apenas uma, declarar a limitação.

- Cobertura: temas de referência cobertos / total de temas relevantes de referência.
- Fidelidade: afirmações sustentadas / afirmações factuais.
- Contradição: afirmações contraditas / afirmações factuais.
- Validade de citações: IDs existentes / IDs citados. É verificação estrutural, não fidelidade semântica.
- Latência: mediana e p95; deltas pareados por pergunta.

Sem anotação ou com denominador zero, manter métrica ausente. Não transformar ausência em zero ou acerto. O avaliador rejeita contagens negativas, cobertura impossível e categorias de afirmações que excedam o total. A anotação final deve ser auditável por tema/afirmação, além do resumo em CSV.

Calcular diferenças temático − tradicional por par; tirar a média das repetições dentro de cada pergunta; bootstrap com reamostragem de perguntas para IC de 95%. Não tratar as três repetições como perguntas independentes. Reportar pares ausentes, tamanho amostral e resultados negativos. Intervalos com apenas uma pergunta não sustentam inferência.

## Aceite científico

O estudo está completo quando os dois métodos executam no corpus validado, os testes passam, o benchmark e parâmetros estão congelados, a referência e anotações estão concluídas, as métricas têm rastreabilidade, e uma reprodução independente segue os comandos documentados. Não é necessário que o método temático seja superior. Não declarar avaliação concluída com respostas apenas geradas.

## Fontes

- Curso: https://ica.ele.puc-rio.br/cursos/ia-generativa-large-language-models/
- Dados e referência bibliográfica: https://amazon-reviews-2023.github.io/
- Dataset card: https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023
- Encoder: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- Gemma no Ollama: https://ollama.com/library/gemma3
- API: https://docs.ollama.com/api/chat
