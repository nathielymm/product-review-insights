# Demonstração local

A interface contém pergunta, seleção de método, resposta e fontes, com escolha entre os três conjuntos principais. Ela reutiliza a recuperação e a geração existentes, sem escrever corpora, índices, respostas experimentais ou métricas. As consultas não são experimentos adicionais do TCC.

## Executar

Na raiz do repositório, com o ambiente local já preparado:

```sh
ollama serve
```

Neste computador, o runtime usado nos experimentos está guardado no projeto. Se `ollama` não estiver no PATH, inicie-o da raiz do repositório com:

```sh
OLLAMA_HOST=127.0.0.1:11434 OLLAMA_NO_CLOUD=1 OLLAMA_MODELS="$PWD/artifacts/ollama-models" artifacts/ollama-runtime/Ollama.app/Contents/Resources/ollama serve
```

Se o Ollama já estiver aberto, use o serviço existente. O modelo `gemma3:4b` precisa estar disponível localmente. Em outro terminal:

```sh
.venv/bin/python scripts/serve_demo.py
```

Abra http://127.0.0.1:8501. Para outra porta, use `--port 8502`. Encerre com Ctrl+C. A interface usa somente a biblioteca padrão do Python e o ambiente existente; não requer instalação de Streamlit ou alteração de dependências.

Os três índices principais declarados em configs/evaluation-freeze.v1.json, incluindo seus encoders locais, precisam existir. A distribuição de código não inclui esses artefatos privados. O serviço escuta apenas em 127.0.0.1 e consulta o Ollama local em 127.0.0.1:11434; não há envio a serviços de nuvem. Não disponibilizar esse servidor diretamente na rede.

## Uso e limites

Selecione o conjunto e o método, escreva a pergunta e clique em “Consultar avaliações”. As respostas da demonstração são geradas em português brasileiro com um contrato de idioma próprio da interface; os comentários originais permanecem em inglês. O prompt e as respostas em inglês dos experimentos congelados não foram alterados. Referências como [E1] abrem os trechos efetivamente incluídos no contexto, com identificador da família. Os textos são apresentados como texto, sem executar HTML recebido do modelo ou das fontes.

O tempo exibido inclui o carregamento do índice/modelo quando necessário e não é comparável diretamente às latências congeladas. Formato inválido e cortes são sinalizados, preservando o texto recebido. Falhas mostram uma mensagem e não geram respostas fictícias ou novas tentativas automáticas. Uma consulta é processada por vez; repetir a pergunta é uma nova consulta demonstrativa.

Não há gravação de histórico ou logs de perguntas pela aplicação. Pergunta e resultado ficam na memória do navegador/servidor durante o processamento; o Ollama mantém o modelo carregado conforme a configuração existente. As fontes do corpus são privadas e devem ser revisadas antes de qualquer compartilhamento. Citações identificáveis não garantem fidelidade semântica. A aplicação apoia exploração de hipóteses, sem validação comercial ou clínica.

## Identificação de produtos

Resposta e fontes mostram nome descritivo e tipo de produto, mantendo grupo e código como referência secundária. demo/product-labels.json deriva das famílias descritivas já registradas em configs/diversity-candidates.draft.json; não é um catálogo oficial ou confirmação de SKU, versão ou fórmula. Nomes ausentes recebem identificação genérica e mantêm o código, sem inventar marca. Esses rótulos são apenas apresentação e não entram na recuperação ou no prompt.

## Leitura das respostas

Respostas estruturadas válidas aparecem em cartões por produto. Cada achado mantém relato, referências, proposta e incerteza nos campos originais, com destaque visual para sugestões e pontos a verificar. O título “Relatos e problemas” também pode conter experiências positivas; a interface não infere uma nova classificação. Limites gerais aparecem ao final. Saídas inválidas continuam visíveis como texto original com aviso, sem reparo ou descarte.

A resposta mostra a quantidade de avaliações únicas citadas e de produtos correspondentes. Vários trechos da mesma avaliação contam uma vez. Fontes incluídas no contexto, mas não citadas, não entram nessa contagem. O resumo fica indisponível quando a estrutura ou a identidade das avaliações não permite contagem confiável; não representa prevalência ou cobertura do corpus.

## Consulta por produto

O seletor Produto permite consultar todos os produtos do conjunto ou uma família específica. As opções são atualizadas quando o conjunto muda. A API valida que a família pertence ao conjunto escolhido. Na consulta individual, somente os vetores dos trechos dessa família entram em um índice temporário em memória; a busca e a seleção de candidatos acontecem dentro desse recorte, antes da escolha dos oito trechos. Não se filtra apenas o resultado final da busca geral. Os dois métodos estão disponíveis.

Os vetores e agrupamentos existentes são reutilizados sem nova indexação em disco ou reagrupamento. O método temático diversifica os grupos existentes dentro da família, sem garantir oito temas distintos. Modelo, orçamento de contexto e limite de geração são os mesmos da demonstração anterior. A consulta individual é uma extensão de uso da interface, sem avaliação científica própria ou comprovação de maior profundidade; resultados e métricas congelados permanecem separados.
