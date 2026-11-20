# Reprodução do projeto

Para instalar e usar a ferramenta com dados públicos, siga o [guia de instalação](installation.md). Os passos abaixo permitem conferir o experimento e recalcular suas métricas a partir dos insumos originais.

## 1. Preparar o ambiente

O ambiente experimental utiliza Python 3.12.14, macOS arm64 e as versões registradas em `requirements.lock.txt`.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python -m pip install --no-deps --no-build-isolation -e .
export OMP_NUM_THREADS=1
export TOKENIZERS_PARALLELISM=false
.venv/bin/python -m pytest -q
```

A instalação da aplicação em outras plataformas está descrita no guia de instalação; a reprodução experimental exige as versões e os arquivos registrados no congelamento.

## 2. Disponibilizar os insumos

Os caminhos e hashes esperados estão em `configs/evaluation-freeze.v2.json` e na configuração vinculada `configs/product-evaluation.v2.approved-not-frozen.json`.

| Insumo | Localização |
|---|---|
| Corpora dos três produtos | `data/processed/product-focused-draft/items/` |
| Índices FAISS, agrupamentos e encoders | `artifacts/product-evaluation-v2/review-candidate/` |
| Referências e unidades de avaliação | Caminhos indicados na configuração |
| Verificações técnicas | `results/product-evaluation-v2/technical-checks/` |
| Respostas, traduções e logs da execução | `results/product-evaluation-v2/final-run/` |
| Anotações e chave de identificação dos métodos | `results/product-evaluation-v2/annotations-v2-human-reviewed/` |

Esses arquivos são locais e não acompanham o repositório. A preparação por `setup_demo.py` cria índices próprios para usar a aplicação, sem substituir os insumos necessários ao recálculo das métricas publicadas.

Para gerar novas respostas, o Ollama deve estar ativo em `127.0.0.1:11434`, com runtime `0.40.11` e modelo `gemma3:4b`, digest `68ceab7e468a31c988b44d5a4984a0e21f58c4f7158c6ce29c1804babac38df7`. Consulte o [comando de inicialização local](local-demo.md).

## 3. Conferir as entradas

```sh
.venv/bin/python scripts/run_product_evaluation_v2.py \
  --config configs/product-evaluation.v2.approved-not-frozen.json --check
```

Acrescente `--runtime` para conferir também o Ollama e o modelo. O comando não gera respostas. O status `inputs_verified_not_frozen` indica a conferência das entradas; o congelamento é definido separadamente em `evaluation-freeze.v2.json`.

Para comparar os 36 contextos predefinidos da interface com os registrados, sem chamar o modelo:

```sh
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  .venv/bin/python scripts/check_demo_v2_contexts.py
```

## 4. Recalcular as métricas

Com os insumos originais disponíveis, escolha um destino que ainda não exista:

```sh
.venv/bin/python scripts/score_product_evaluation_v2.py \
  --config configs/product-evaluation.v2.approved-not-frozen.json \
  --runs results/product-evaluation-v2/final-run \
  --output results/product-evaluation-v2/metrics-reproduction-new \
  --export \
  --annotations results/product-evaluation-v2/annotations-v2-human-reviewed/annotations.private.json \
  --blind-key results/product-evaluation-v2/annotations-v2-human-reviewed/blinding-key.private.json
```

Compare o `aggregates.json` produzido com `docs/product-evaluation.v2-results.json`. O cálculo utiliza os 36 casos principais e mantém as 24 repetições diagnósticas fora dos denominadores de qualidade. As métricas dependem das anotações fornecidas; o comando não realiza novos julgamentos semânticos.

## 5. Executar outra rodada

Esta etapa é opcional para quem deseja gerar novas respostas. Use destinos novos para preservar a execução original:

```sh
.venv/bin/python scripts/run_product_evaluation_v2.py \
  --config configs/product-evaluation.v2.approved-not-frozen.json \
  --run-frozen \
  --freeze configs/evaluation-freeze.v2.json \
  --output results/product-evaluation-v2/reproduction-run-new \
  --token-ledger results/product-evaluation-v2/reproduction-token-probes-new.private.jsonl
```

Novas respostas podem diferir das registradas e precisam de anotações próprias antes de serem avaliadas. Não reutilize automaticamente as anotações da execução original.
