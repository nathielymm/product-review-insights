# Protocolo experimental — versão de desenvolvimento

## Hipótese e comparação

O agrupamento pode aumentar a diversidade das evidências e a cobertura dos insights, com possível perda de relevância ou aumento do custo. A hipótese não pressupõe ganho. Comparação pareada no mesmo corpus, perguntas, encoder, FAISS, Gemma, prompt, número máximo de trechos e orçamento de contexto. O tamanho real do contexto e a quantidade de evidências podem diferir e devem ser reportados.

O enriquecimento consiste em diversidade por cluster nos top-80 candidatos, não em uma segunda fonte de conhecimento. Uma ablação futura poderá comparar com MMR; ela não integra o experimento principal atual. Os grupos devem ser inspecionados por termos e representantes; ajustar K apenas no desenvolvimento. Registrar coerência e estabilidade em mais de uma seed antes de congelar K.

## Dados e privacidade

Usar o Parquet fornecido, registrar SHA-256 e confirmar procedência antes da apresentação final. O esquema não traz categoria explícita. O dataset é publicamente disponibilizado pelo McAuley Lab, mas disponibilidade pública não equivale a autorização irrestrita para redistribuição. Registrar as condições da fonte antes de distribuir qualquer derivado. Não redistribuir corpus, trechos, respostas ou IDs de consumidores. O código remove user_id e imagens; redação heurística de texto requer revisão manual para nomes/endereço e outros identificadores residuais.

A amostra por hash é uniforme entre avaliações válidas e únicas; não estratificada. Reportar distribuição de notas e idioma. Não traduzir avaliações no experimento principal. Verificar idioma na amostra e definir regra de inclusão antes do teste. A preparação não utiliza perguntas nem rótulos de avaliação.

## Perguntas e referência

As 10 perguntas em questions.dev.json são exclusivamente de desenvolvimento. O conjunto de 30 perguntas em questions.eval.draft.json é uma proposta, ainda não um benchmark validado. A usuária/revisora deve revisar escopo, redundância e respondibilidade. Congelar arquivo e hash antes da primeira execução final e não otimizar parâmetros com seus resultados.

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
