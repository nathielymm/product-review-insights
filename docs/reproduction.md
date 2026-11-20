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
.venv/bin/social-listening prepare data/raw/all_beauty.supplied.parquet
HF_HOME=artifacts/huggingface .venv/bin/social-listening build
```

A primeira indexação baixa o encoder. As seguintes podem usar o cache com HF_HUB_OFFLINE=1. O encoder exato é salvo em artifacts/pilot/encoder; as consultas carregam apenas esse snapshot local. metadata.json registra hashes do corpus, índice, trechos e arquivos do encoder. Preserve esses arquivos localmente para reproduzir a execução. Não indexar dados não revisados como se estivessem anonimizados.

As pastas de build/preparação podem ser sobrescritas; use destinos novos com --output para preservar experimentos anteriores. Execuções e exportações cegas exigem diretórios novos, evitando sobrescrita acidental.

## Ollama e Gemma

O Ollama oficial foi extraído em artifacts/ollama-runtime, sem instalação em Applications nem alteração do PATH. Sua primeira inicialização cria uma chave em ~/.ollama. O servidor deve escutar somente no loopback, com a nuvem desativada:

```sh
OLLAMA_HOST=127.0.0.1:11434 OLLAMA_NO_CLOUD=1 OLLAMA_MODELS="$PWD/artifacts/ollama-models" artifacts/ollama-runtime/Ollama.app/Contents/Resources/ollama serve
```

Em outro terminal, ainda na raiz:

```sh
artifacts/ollama-runtime/Ollama.app/Contents/Resources/ollama pull gemma3:4b
.venv/bin/social-listening query 'What complaints concern packaging?' --method traditional
.venv/bin/social-listening query 'What complaints concern packaging?' --method thematic
```

Em outro computador, instalar o Ollama pelo site oficial e usar `ollama serve`/`ollama pull`. O nome do modelo é uma tag mutável; preservar o digest registrado nas execuções e o modelo local. Nunca substituir por um modelo :cloud no experimento.

## Desenvolvimento, benchmark e anotação

```sh
.venv/bin/social-listening run --questions configs/questions.dev.json --output results/dev-001 --repetitions 3
.venv/bin/social-listening summarize results/dev-001/runs.jsonl
.venv/bin/social-listening blind results/dev-001/runs.jsonl --output results/dev-001-blind
```

Não interpretar a execução de desenvolvimento como avaliação final. Revisar o arquivo questions.eval.draft.json, preparar a referência humana, congelar o benchmark e copiar para questions.eval.json antes da execução final. Não incluir citações ou textos reais no Git para facilitar a reprodução; forneça manifestos agregados e instruções de acesso à fonte.

Preencher annotations.csv conforme docs/protocol.md e guardar notas por afirmação/tema. Entregar à revisora apenas blind.json e annotations.csv; key.private.json revela os métodos.

```sh
.venv/bin/social-listening evaluate results/dev-001/runs.jsonl --annotations results/dev-001-blind/annotations.csv --key results/dev-001-blind/key.private.json
```

As métricas humanas ficam ausentes até o preenchimento. A precisão de IDs de citações não substitui revisão da evidência. Para medir a partida fria, descarregar o modelo via Ollama e executar uma medição separada; o runner principal faz aquecimento e registra load_duration em cada resposta.

## Git local e revisão

Commits pequenos por entrega. A identidade dos commits é genérica, sem nome/email pessoal. Nenhum remote deve ser configurado, e nenhum push deve ser executado antes da revisão da usuária. Antes de criar o GitHub privado, conferir arquivos rastreados e ausência de corpus, respostas, modelos, tokens e dados acadêmicos pessoais. A matrícula e nomes permanecem em branco no README.
