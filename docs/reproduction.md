# Reprodução local — v2 por produto

Este guia descreve a avaliação por produto e a interface atuais.

## Ambiente

O ambiente registrado usa Python 3.12.14 no macOS arm64. O projeto declara Python >=3.11, mas isso não certifica o lock em todas as versões/arquiteturas. Em uma instalação nova:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python -m pip install --no-deps --no-build-isolation -e .
.venv/bin/python -m pytest -q
```

O lock registra versões, sem hashes dos wheels; instalação em ambiente limpo/outra arquitetura ainda precisa ser verificada. As bibliotecas registradas na configuração v2 e os artefatos locais devem corresponder para reproduzir a execução. Mantenha `OMP_NUM_THREADS=1` e `TOKENIZERS_PARALLELISM=false`; não é necessário monitorar processos, CPU ou memória.

## O que acompanha o código

O Git contém implementação, testes, configurações, hashes e agregados. Parquet, corpora, índices/encoders, modelos, fontes individuais, anotações e respostas não são distribuídos. Não é possível reproduzir os julgamentos semânticos apenas executando o código. Diferencie:

- Usar a interface: exige índices/encoders individuais e modelo local, conforme [guia da interface](local-demo.md).
- Recalcular métricas já anotadas: exige runs, traduções, logs técnicos e as anotações/chave finais, além dos demais insumos conferidos pelo executor de métricas.
- Reconstruir a preparação ou gerar outra rodada: exige a fonte e cadeia de artefatos privados, planejamento de novos destinos e verificação de identidades. Não sobrescreve nem substitui o experimento congelado.

A procedência exata do Parquet fornecido em relação ao dataset oficial declarado continua uma limitação. A referência é parcial e a revisão humana não é independente.

## Entradas da avaliação congelada

A autoridade é `configs/evaluation-freeze.v2.json`. Ele vincula a configuração historicamente chamada `configs/product-evaluation.v2.approved-not-frozen.json`; o nome/status interno anterior foi preservado. Não altere flags ou hashes para fazer outro conjunto de arquivos passar como o original.

A configuração lista os corpora por produto em `data/processed/product-focused-draft/items/`, índices em `artifacts/product-evaluation-v2/review-candidate/`, perguntas, referências, unidades, sondagens e arquivos de implementação. Os corpora têm 613, 473 e 123 avaliações; os índices têm 613, 474 e 123 trechos. Usam-se quatro agrupamentos dentro de cada produto. Referências e unidades são julgamentos locais revisados parcialmente, não rótulos deduzidos por identificador.

A preparação histórica dos corpora por identificador está em `scripts/prepare_product_cases.py`, que exige destino novo e deriva dos corpora revisados anteriores. A indexação utiliza `product_review_insights.retrieval.build`, com parâmetros/metadados registrados nos índices. Reconstruir o caminho completo a partir de um novo Parquet ainda não foi certificado em ambiente limpo; esse procedimento depende dos artefatos privados de origem/revisão e não deve ser anunciado como reprodução automática apenas pelo ZIP.

Para conferir as entradas locais da execução, sem gerar respostas:

```sh
.venv/bin/python scripts/run_product_evaluation_v2.py --config configs/product-evaluation.v2.approved-not-frozen.json --check
```

O resultado `inputs_verified_not_frozen` refere-se à conferência da configuração histórica. O congelamento externo já existe; esse comando não o cria nem autoriza outra execução. Com `--runtime`, também se verifica o Ollama ativo/digest esperado, sem geração. A interface atual valida os insumos que utiliza, dispensando os arquivos privados de pontuação que o executor completo exige.

## Modelo e demonstração

O modelo é `gemma3:4b`, digest `68ceab7e468a31c988b44d5a4984a0e21f58c4f7158c6ce29c1804babac38df7`, no runtime registrado `0.40.11`. A tag sozinha é mutável. O runtime/modelo exatos não acompanham o Git; preserve seus arquivos locais ou obtenha uma distribuição verificável. Não execute `pull` para substituir silenciosamente o modelo congelado.

As instruções de início local estão no [guia da interface](local-demo.md). Modelo, geração e tradução são locais. Perguntas avaliadas reutilizam as entradas inglesas/aspectos congelados; perguntas livres têm planejamento demonstrativo separado, não métricas experimentais.

## Recálculo das métricas existentes

Com todos os insumos privados originais presentes, use um destino que ainda não exista:

```sh
.venv/bin/python scripts/score_product_evaluation_v2.py \
  --config configs/product-evaluation.v2.approved-not-frozen.json \
  --runs results/product-evaluation-v2/final-run \
  --output results/product-evaluation-v2/metrics-reproduction-new \
  --export \
  --annotations results/product-evaluation-v2/annotations-v2-human-reviewed/annotations.private.json \
  --blind-key results/product-evaluation-v2/annotations-v2-human-reviewed/blinding-key.private.json
```

O executor verifica o vínculo entre runs, unidades, anotações e grade, preservando todos os 36 casos principais e excluindo as 24 repetições diagnósticas dos denominadores de qualidade. Compare o novo `aggregates.json` com `docs/product-evaluation.v2-results.json`; não exporte textos ou notas individuais ao Git. A inspeção das seis diferenças diagnósticas está em [relatório separado](product-evaluation.v2-diagnostic-inspection.md).

## Conferência da recuperação da interface

Com os índices locais e o run principal disponíveis, reconstrua os contextos das 36 perguntas/métodos predefinidos, sem consultar o Gemma:

```sh
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 OMP_NUM_THREADS=1 TOKENIZERS_PARALLELISM=false .venv/bin/python scripts/check_demo_v2_contexts.py
```

O comando usa o encoder local, verifica a grade e a identidade do arquivo de execução, e compara pergunta inglesa, fontes/ordem e fingerprint dos candidatos com o principal. Não escreve resultados ou faz geração.

## Novas gerações e anotações

O runner `scripts/run_product_evaluation_v2.py` exige `--run-frozen`, `--freeze`, `--output` e `--token-ledger`, além da configuração, e recusa um destino existente. Ele confere os insumos e o runtime, mantém falhas e não faz escolha da melhor resposta. Seu uso para outra rodada gera novos dados; não é necessário para recalcular as métricas ou testar a integração de recuperação da interface.

A preparação de fichas está em `scripts/score_product_evaluation_v2.py --prepare-annotations`, com os mesmos argumentos de configuração/runs e um novo destino. As fichas começam pendentes. Preencher e conferir afirmações, alvos e propostas é trabalho de anotação semântica, com escopo humano delimitado; não há atribuição automática de suporte por IDs. Alterações de protocolo requerem nova versão, preservando os resultados anteriores.

## Estado da validação

A suíte local e o recálculo agregado foram verificados no ambiente existente. Os 36 contextos de perguntas avaliadas também foram reconstruídos offline pelo mesmo helper usado na interface e coincidiram com os contextos congelados e fingerprints de candidatos. A validação de idioma/formato e integridade não certifica fidelidade factual. Uma nova consulta ao vivo pode produzir texto diferente mesmo com entrada igual, conforme os diagnósticos documentados.

## Entrega e Git

Dados acadêmicos permanecem em branco até serem fornecidos. O repositório no GitHub é privado. Não versionar dados brutos, segredos, modelos, respostas ou anotações individuais. Consulte a [estrutura do projeto](structure.md) para identificar os arquivos da versão atual.
