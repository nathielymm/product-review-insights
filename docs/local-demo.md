# Interface local — avaliação por produto v2

A interface usa os três produtos da v2: escova GranNaturals (613 avaliações), shampoo Pure Body Naturals Argan (473) e máscara Bold Lash (123). A consulta ocorre em um índice individual, com quatro agrupamentos internos ao produto, sem consulta conjunta a famílias ou reconstrução de índices.

## Iniciar

Na raiz do repositório, use o ambiente do projeto e o Ollama local com o modelo e runtime registrados na configuração v2. Neste computador:

```sh
OLLAMA_HOST=127.0.0.1:11434 OLLAMA_NO_CLOUD=1 OLLAMA_MODELS="$PWD/artifacts/ollama-models" artifacts/ollama-runtime/Ollama.app/Contents/Resources/ollama serve
```

Se esse serviço já estiver ativo, utilize-o. Em outro terminal:

```sh
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python scripts/serve_demo.py
```

Abra http://127.0.0.1:8501. Outra porta pode ser escolhida com `--port 8503`; encerre com Ctrl+C. O servidor só escuta em loopback. Não há instalação de Streamlit ou nova dependência de interface.

O código público não inclui dados, índices ou modelos. Além do código e das configurações versionadas, a demonstração requer os três diretórios de índice em `artifacts/product-evaluation-v2/review-candidate/`, com `metadata.json`, `index.faiss`, `chunks.jsonl`, `clusters.npy` e os snapshots `encoder/`, bem como o Gemma no Ollama local. Configuração, perguntas, código reutilizado e metadados são conferidos contra a v2; o Retriever valida os arquivos do índice e encoder ao carregá-los. O modelo ativo deve corresponder ao digest e à versão de runtime registrados. Não são necessárias anotações semânticas privadas para usar a interface.

Se o ledger de sondagens prévias em `results/product-evaluation-v2/technical-checks/runtime-token-probes.private.jsonl` estiver disponível, ele é lido e verificado pelo hash. Sem ele, o orçamento é conferido por sondagens técnicas em memória. O aplicativo não escreve no ledger congelado nem em outros arquivos de resultados.

## Perguntas e métodos

Escolha um produto, um método e uma das seis perguntas do estudo, ou escreva outra pergunta. Ao trocar o produto, a pergunta é limpa e as opções são atualizadas. Editar um exemplo o transforma em pergunta livre.

Nas perguntas avaliadas, o servidor reutiliza exatamente o equivalente inglês, as cinco consultas por aspectos, RRF com constante 60, até 16 candidatos por aspecto, deduplicação por avaliação e limite de 80 candidatos. O tradicional seleciona as primeiras oito avaliações do ranking comum; o temático seleciona representantes dos grupos locais e completa pelo mesmo ranking. O mesmo `prepare_attempt` da execução v2 compõe o contexto.

Na pergunta livre, uma chamada local de planejamento traduz a pergunta para inglês e propõe cinco consultas por aspectos. Essa entrada passa pelo mesmo algoritmo de fusão/seleção, mas é um caminho demonstrativo adicional: perguntas e aspectos não foram predefinidos ou pontuados no experimento. O planejador pode interpretar incorretamente a intenção; seus resultados não ampliam a grade experimental.

## Geração e apresentação

A resposta usa a função original de geração em inglês e seus parâmetros congelados. Uma segunda etapa traduz somente observações, propostas, incertezas e limites para português. Fontes, identidades e citações permanecem iguais, e o inglês é conferido para detectar alteração durante a tradução. “Ver original em inglês” permite consultá-lo.

A resposta aparece em cartões com relatos, sugestões e pontos a verificar. As referências abrem as fontes efetivamente incluídas no contexto, apresentadas em inglês. A quantidade de avaliações considera somente as citadas, deduplicadas por avaliação; não mede representatividade ou cobertura de todo o corpus. Os textos são inseridos como texto, sem executar HTML recebido.

Se a tradução falhar, a interface informa isso e mostra o original em inglês. Se o inglês vier fora do formato, o texto recebido continua visível, sem reparo ou nova geração automática. Cortes de inglês ou tradução são sinalizados. Não há histórico persistido de perguntas ou respostas. A aplicação permite uma consulta por vez, sem substituir resultados do TCC.

O orçamento de tokens é verificado pelo transporte da v2: entradas novas podem exigir sondagem técnica de um token, separada da resposta. O tempo na página inclui carga, planejamento quando necessário, sondagens, geração e tradução; não deve ser comparado diretamente às medianas experimentais de geração inglesa.

## Reprodução e verificações

Consulte [reprodução da v2](reproduction.md) e [resultados congelados](product-evaluation.v2-results.md). Os testes usam fontes/modelos simulados para verificar limites, inglês, tradução, citações e isolamento. A integração offline também conferiu os 36 contextos das perguntas avaliadas contra os registrados, sem gerar novas respostas. Consultas ao vivo são verificações demonstrativas separadas, não novas métricas de qualidade.
