# Reprodução local

## Ambiente

Python 3.11 ou superior; o ambiente de desenvolvimento foi criado com Python 3.12.14 no macOS arm64. Não usar o Python 3.9 do sistema. A pasta `.venv` contém as dependências isoladas e não é versionada.

Em uma instalação nova, a partir da raiz do repositório:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python -m pip install --no-deps --no-build-isolation -e .
.venv/bin/python -m pytest -q
```

O lock registra as versões instaladas neste desenvolvimento; não inclui hashes dos wheels e deve ser validado novamente em outra arquitetura. O runtime inicial apresentou encerramento nativo ao combinar paralelismo de Torch/FAISS; o pacote define OMP_NUM_THREADS=1 e TOKENIZERS_PARALLELISM=false antes dos imports nativos. Manter esses parâmetros iguais nas duas condições e registrar qualquer alteração. Não foi necessário alterar bibliotecas do sistema.

## Preparação e indexação

Guardar o Parquet localmente em data/raw/all_beauty.supplied.parquet, ou indicar outro caminho. Dados, textos processados, modelos e respostas são ignorados pelo Git.

```sh
.venv/bin/product-review-insights prepare data/raw/all_beauty.supplied.parquet
HF_HOME=artifacts/huggingface .venv/bin/product-review-insights build
```

A primeira indexação baixa o encoder. As seguintes podem usar o cache com HF_HUB_OFFLINE=1. O encoder exato é salvo em artifacts/pilot/encoder; as consultas carregam apenas esse snapshot local. metadata.json registra hashes do corpus, índice, trechos e arquivos do encoder. Preserve esses arquivos localmente para reproduzir a execução. Não indexar dados não revisados como se estivessem anonimizados.

A preparação antiga do piloto e os builds podem sobrescrever destinos; prepare-study exige destino novo. use destinos novos com --output para preservar experimentos anteriores. Execuções e exportações cegas exigem diretórios novos, evitando sobrescrita acidental.

## Ollama e Gemma

O Ollama oficial foi extraído em artifacts/ollama-runtime, sem instalação em Applications nem alteração do PATH. Sua primeira inicialização cria uma chave em ~/.ollama. O servidor deve escutar somente no loopback, com a nuvem desativada:

```sh
OLLAMA_HOST=127.0.0.1:11434 OLLAMA_NO_CLOUD=1 OLLAMA_MODELS="$PWD/artifacts/ollama-models" artifacts/ollama-runtime/Ollama.app/Contents/Resources/ollama serve
```

Em outro terminal, ainda na raiz:

```sh
artifacts/ollama-runtime/Ollama.app/Contents/Resources/ollama pull gemma3:4b
.venv/bin/product-review-insights query 'What complaints concern packaging?' --method traditional
.venv/bin/product-review-insights query 'What complaints concern packaging?' --method thematic
```

Em outro computador, instalar o Ollama pelo site oficial e usar `ollama serve`/`ollama pull`. O nome do modelo é uma tag mutável; preservar o digest registrado nas execuções e o modelo local. Nunca substituir por um modelo :cloud no experimento.

## Desenvolvimento, benchmark e anotação

```sh
.venv/bin/product-review-insights run --questions configs/questions.dev.json --output results/dev-001 --repetitions 3
.venv/bin/product-review-insights summarize results/dev-001/runs.jsonl
.venv/bin/product-review-insights blind results/dev-001/runs.jsonl --output results/dev-001-blind
```

Não interpretar a execução de desenvolvimento como avaliação final. Revisar o arquivo questions.eval.draft.json, preparar a referência humana, congelar o benchmark e copiar para questions.eval.json antes da execução final. Não incluir citações ou textos reais no Git para facilitar a reprodução; forneça manifestos agregados e instruções de acesso à fonte.

O rascunho atual tem 16 perguntas e pressupõe produto/recorte definido. Não executá-lo diretamente no índice global: o runner exige --cohort e rejeita índices globais ou de outro conjunto. Ver docs/product-scopes.md antes de construir os corpora de avaliação.

Para reproduzir a exploração dos recortes, sem consultar os modelos ou usar respostas de avaliação:

```sh
.venv/bin/python scripts/profile_products.py data/raw/all_beauty.supplied.parquet
```

O script conta avaliações válidas e únicas por parent_asin, lista os 40 produtos com mais avaliações e seleciona até oito exemplos por nota por produto usando hash determinístico. summary.json e examples.private.json ficam em results/product-profile, fora do Git. Os exemplos são de inspeção qualitativa e não estimam a prevalência dos temas. Nenhum identificador de usuário é lido. A distribuição de notas é apenas um sinal de diversidade de experiências, não uma classificação de sentimento.

Para reproduzir o mapeamento de categorias, baixar o catálogo oficial na revisão registrada, mantendo-o fora do Git:

```sh
curl -fL 'https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/2b6d039ed471f2ba5fd2acb718bf33b0a7e5598e/raw_meta_All_Beauty/full-00000-of-00001.parquet' -o data/raw/meta_all_beauty.parquet
.venv/bin/python scripts/map_categories.py
.venv/bin/python scripts/shortlist_categories.py
```

O SHA-256 esperado do catálogo é 14815cf1312a0d847364866e6876c8c73738993469067242870774c372c04387. Conferir o hash antes de comparar com docs/category-map-summary.json. As regras produzem uma classificação exploratória por título, pois as subcategorias oficiais estão vazias. Os dados detalhados ficam em results/category-map; os grupos candidatos de configs/category-cohorts.draft.json ainda não foram selecionados nem aplicados aos índices.

Para explorar as três condições de variedade, usando os arquivos locais e o encoder já salvo:

```sh
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python scripts/explore_diversity.py
```

O extra analysis do pyproject inclui langdetect 1.0.9; o lock registra esse pacote e six. O script identifica inglês com seed fixa e score mínimo 0,90, limpa HTML e restringe o tamanho dos textos a 20–200 palavras. Toda a detecção e codificação ocorre localmente. Não confundir o score do detector com garantia de idioma. O cache com --reuse-pools só é reutilizado se fonte, critérios/código de preparação, versão do detector e hashes dos arquivos coincidirem.

A configuração de candidatos fica em configs/diversity-candidates.draft.json. O script salva comentários, embeddings e IDs das amostras em results/diversity-exploration, fora do Git. O resumo agregado e a leitura dos indicadores estão em docs/diversity-exploration-summary.json e docs/diversity-candidates.md. Nenhuma resposta do Gemma é gerada nessa etapa. Não usar a exploração como avaliação final dos RAGs; condições, perguntas, unidade de comparação e validação temática ainda precisam ser fechadas.

Para preparar a revisão qualitativa dos três conjuntos prioritários:

```sh
.venv/bin/python scripts/prepare_theme_review.py
# Ler os arquivos privados, revisar e registrar a codificação local.
.venv/bin/python scripts/summarize_theme_review.py
```

O primeiro script gera seis comentários por grupo de produto e recupera os ASINs dos itens na fonte. O segundo exige a codificação existente em results/theme-review/assistant-coding.private.json, verifica os hashes e a identidade de cada registro e agrega os resultados. Não gera rótulos ausentes. Essa codificação foi proposta pelo assistente e requer revisão da usuária; não é referência humana independente. Os textos e rótulos por comentário ficam fora do Git, portanto reproduzir a agregação exata requer os arquivos privados locais. O resumo público e as limitações estão em docs/theme-consistency-summary.json e docs/theme-consistency-review.md.

Preencher annotations.csv conforme docs/protocol.md e guardar notas por afirmação/tema. Entregar à revisora apenas blind.json e annotations.csv; key.private.json revela os métodos.

```sh
.venv/bin/product-review-insights evaluate results/dev-001/runs.jsonl --annotations results/dev-001-blind/annotations.csv --key results/dev-001-blind/key.private.json
```

As métricas humanas ficam ausentes até o preenchimento. A precisão de IDs de citações não substitui revisão da evidência. Para medir a partida fria, descarregar o modelo via Ollama e executar uma medição separada; o runner principal faz aquecimento e registra load_duration em cada resposta.

## Git local e revisão

Commits pequenos por entrega coerente, conforme AGENTS.md; não criar um commit por aprovação ou rodada da conversa. O mapa de marcos está em docs/development-history.md. A identidade dos commits é genérica, sem nome/email pessoal. Nenhum remote deve ser configurado, e nenhum push deve ser executado antes da revisão da usuária. Antes de criar o GitHub privado, conferir arquivos rastreados e ausência de corpus, respostas, modelos, tokens e dados acadêmicos pessoais. A matrícula e nomes permanecem em branco no README.

## Corpora do estudo alinhado

Depois de reproduzir os pools de diversidade e reservar a auditoria, executar:

```sh
.venv/bin/product-review-insights prepare-study
.venv/bin/product-review-insights build --corpus data/processed/study-v1/development/development_disjoint/corpus.jsonl --output artifacts/study-v1/development-check --config configs/study-development-smoke.json
```

A configuração ativa é configs/study-scope.json. A preparação verifica hashes dos arquivos privados e falha se divergirem; a reprodução exata requer os mesmos arquivos locais. Os 40 corpora e manifestos ficam em data/processed/study-v1, fora do Git. Não reutilizar o destino existente: alterações após revisão exigem novo snapshot. Ver docs/study-preparation-summary.json.

O build acima é integração no desenvolvimento, sem hiperparâmetros finais. Para execução futura de perguntas de avaliação, construir um índice por corpus com a configuração congelada e passar --index e --cohort correspondente ao comando run. Nunca usar o índice development-check como índice de avaliação. O rascunho das perguntas e a referência ainda precisam ser fechados.

## Revisão direcionada concluída

A versão atual é indicada por configs/corpus-current.json. Ver docs/final-corpus-qa.md para gerar a revisão a partir do snapshot inicial, com exclusões, redação de assinatura e reconstrução dos subconjuntos. Usar os corpora de data/processed/study-v2-qa-final em novos builds. Os caminhos study-v1 anteriores documentam a preparação histórica.

## Preparação da rubrica por unidades

Depois da aprovação dos três pacotes revisados, executar scripts/prepare_scoring_reference.py com --output apontando para um novo diretório. O comando gera unidades e disponibilidade de apoios conhecidos nos subconjuntos, sem respostas de modelos ou notas humanas. Ver docs/scoring-rubric.md e configs/scoring-current.draft.json. O avaliador legado por contagens pertence ao piloto e não substitui esta anotação por unidade.

## Seleção operacional concluída no desenvolvimento

O estado atual está em configs/development-current.json. scripts/select_development_parameters.py compara clusters e contexto apenas no split development, validando corpus e cache. scripts/probe_development_generation.py testa o Ollama local nesse mesmo split e preserva respostas brutas. Usar o plano configs/development-selection-plan.json e destinos novos, conforme docs/development-parameter-selection.md. O servidor e o modelo foram encerrados/descarregados ao concluir este piloto; reiniciá-los com as instruções locais acima antes de novas gerações.

A saída estruturada separa grupos e citações. Seu validador rejeita referências de outra família e JSON inválido, sem corrigir conteúdo factual; o resultado bruto é preservado. O contrato é comum aos dois métodos. A versão atual ainda aguarda congelamento final junto com rubrica e referências elegíveis.

## Avaliação integrada sem monitoramento de processos

O fluxo atual usa run-frozen, blind-study e score-study, conforme docs/evaluation-freeze.md e configs/evaluation-current.json. A coleta de memória, CPU por processo e listagem de processos foi removida; os custos são descritos por tempos e tokens. Não há necessidade de ampliar permissões do sistema para monitoramento. Dados, chaves de revisão e anotações individuais permanecem locais e ignorados pelo Git.

## Métricas da avaliação principal anotada

Com os artefatos privados locais e as fichas anotadas, exporte somente agregados para um destino novo:

```sh
.venv/bin/python scripts/report_primary_evaluation.py --output results/evaluation-v1/reproducao-agregada.json
```

O comando valida o congelamento, todos os registros e a conclusão da anotação antes de liberar comparações. Recusa destino existente. O relatório registrado é docs/primary-evaluation-results.v1.json; a discussão está em docs/primary-evaluation-results.v1.md. As notas são do assistente com revisão humana parcial de interpretações, não referência independente. Os resultados dependem das fichas locais; a distribuição de código-fonte não contém dados nem notas individuais.

## Agregados da sensibilidade v1

A grade concluída e seus limites estão em [sensitivity-results.v1.md](sensitivity-results.v1.md). Com os 27 índices, runs e fichas privadas locais completos, execute `.venv/bin/python scripts/report_sensitivity_evaluation.py --output results/sensitivity-v1-execution/nova-reproducao.json`. O destino deve ser novo. O exportador verifica o congelamento e exige todas as anotações antes de comparar métodos. O JSON público contém somente agregados e hashes; os artefatos privados necessários não são distribuídos no código-fonte.
