# Avaliação integrada e congelamento v1

A avaliação foi simplificada conforme a decisão da usuária: medir tempos e tokens, sem listar processos, coletar memória ou solicitar permissões de monitoramento. A dependência direta de psutil foi retirada do projeto; o lock histórico ainda pode registrar o pacote instalado, mas o fluxo de avaliação não o usa para inspecionar processos.

## Estado desta entrega

- 14 perguntas e 179 unidades da referência auditada vinculadas às cinco famílias de cada conjunto.
- Três índices principais preparados e verificados: 547, 1.405 e 1.891 avaliações.
- Trinta corpora vinculados ao protocolo: três principais e 27 de sensibilidade.
- Código, ambiente, encoder, configurações, perguntas, referências e hashes dos corpora registrados no congelamento.
- Digest do Gemma 3 4B e versão do Ollama conferidos pelo runner antes da geração; troca de modelo invalida o runset.
- Nenhuma resposta final foi gerada nesta preparação. Os 53 testes passaram com dados sintéticos e sem servidor de modelo.

O congelamento é técnico: registra as regras antes das respostas. Não transforma a referência em exaustiva, não cria anotação independente nem afirma aprovação humana de cada detalhe novo da implementação de pontuação.

## Como as notas se ligam às respostas

Cada execução fica vinculada à versão congelada, corpus, pergunta, método e repetição. A exportação de revisão oculta método, repetição, tempos, scores de busca e clusters. Há uma chave privada ligando cada item revisado às tentativas originais.

Respostas com pergunta, texto, evidências e estado técnico exatamente iguais podem compartilhar uma anotação. Os tempos de cada tentativa permanecem separados. Assim, repetições idênticas não exigem repetir a revisão nem viram novas observações humanas independentes.

O formulário por resposta registra:

- unidades cobertas nos trechos recuperados e na resposta, separadamente;
- trechos exatos de apoio, família e IDs das unidades;
- afirmações sustentadas, contraditas ou sem suporte, com julgamento de citações;
- critérios separados para propostas e para os dois controles.

Para creditar uma unidade na resposta, a anotação deve incluir um trecho da resposta e uma passagem presente no contexto realmente fornecido. O programa verifica essas ligações, mas a decisão de que o texto sustenta a afirmação continua sendo uma tarefa de revisão. Não existe correção automática baseada apenas em palavras iguais.

Anotação ausente fica sem nota; denominador vazio fica não aplicável. Não se publica comparação final de qualidade enquanto houver revisão pendente ou execução incompleta. Evidência adicional pode ser válida para fidelidade; uma alteração de elegibilidade/denominador exige atualização de referência por caso aplicada igualmente aos dois métodos, antes de revelar a chave.

## Falhas também fazem parte do registro

Falhas de chamada ao modelo preservam a tentativa e o contexto, sem resposta inventada. Três falhas consecutivas interrompem o caso, mantendo o arquivo parcial identificado como incompleto. Não há repetição automática escondida.

Respostas não vazias com JSON inválido ou corte de saída são preservadas para revisão. Resposta vazia de tentativa fracassada deve ser anotada explicitamente como tarefa não atendida; não deve ser excluída nem receber acerto por abstenção. Tempos incluem registros de todas as tentativas, distinguindo falhas de API.

## Recursos medidos

Tempos de busca, geração e total são registrados por tentativa, além dos tokens de entrada/saída informados pelo Ollama. Aquecimento fica separado. Medidas ausentes de tokens continuam ausentes, não zero. Tokens representam volume processado, não energia ou custo financeiro.

O tempo de construção disponível é o do pipeline compartilhado de indexação, incluindo agrupamento. Não temos uma medição isolada do custo adicional do agrupamento versus um build tradicional; não atribuir custo zero ao enriquecimento por esse motivo. Não há medição de memória ou GPU nesta versão.

## Execução prevista, em etapas

| Etapa | Corpora | Repetições por método/pergunta | Respostas previstas |
|---|---:|---:|---:|
| Principal | 3 | 3 | 252 |
| Sensibilidade | 27 | 1 | 756 |

A execução principal vem primeiro. A grade secundária tem uma passagem por método para limitar custo e não estima variabilidade de repetição. Todas as amostras e sementes permanecem declaradas; não selecionar apenas resultados favoráveis. O runner executa um caso solicitado por vez, sem iniciar automaticamente toda a grade.

O total potencial de 1.008 tentativas não equivale ao número de itens únicos para revisão: duplicatas exatas podem compartilhar anotação, e a quantidade real só será conhecida após a geração. As 58 combinações factuais de pergunta/subconjunto sem apoio conhecido continuam explícitas; não lhes atribuir falha automática nem afirmar ausência de tema.

## Comandos da nova avaliação

Na raiz do repositório, iniciar o Ollama local conforme docs/reproduction.md. A chamada usa apenas loopback e modelo já baixado, sem monitoramento de processos.

```sh
# Um caso principal; este comando gera respostas reais.
.venv/bin/product-review-insights run-frozen --case main/compact_mascaras --output results/evaluation-v1/mascaras

# Preparar a revisão sem mostrar o método.
.venv/bin/product-review-insights blind-study results/evaluation-v1/mascaras/runs.jsonl --output results/evaluation-v1/mascaras-review

# Após revisar o formulário privado, calcular e salvar em um arquivo novo.
.venv/bin/product-review-insights score-study results/evaluation-v1/mascaras/runs.jsonl --review results/evaluation-v1/mascaras-review --output results/evaluation-v1/mascaras-review/scores-v1.private.json
```

Os outros casos principais são main/intermediate_hair_disjoint e main/varied_disjoint. Campos e arquivos individuais ficam fora do Git. Guardar snapshots dos formulários em cada rodada de revisão; o relatório inclui o hash da anotação usada.

Os índices de sensibilidade podem ser derivados das mesmas entradas congeladas:

```sh
.venv/bin/product-review-insights build-frozen-index --case sensitivity/n20/seed11/compact_mascaras --output artifacts/evaluation-v1/sensitivity-n20-seed11-mascaras
```

Em seguida, run-frozen aceita --index com esse caminho e --case correspondente. O comando legado evaluate continua disponível para o piloto antigo, mas a avaliação atual usa score-study.

## Rastreabilidade e reprodução

Estado atual: configs/evaluation-current.json. Manifesto: configs/evaluation-freeze.v1.json. Registro privado: results/evaluation-freeze/v1/registry.private.json. A fonte das regras permanece em docs/scoring-rubric.md e no próprio snapshot privado congelado.

freeze-evaluation prepara um novo snapshot e recusa destinos existentes. Reproduzir em outra instalação exige os dados locais, encoder, versões de dependências e entradas correspondentes; diferenças de ambiente pedem uma nova versão documentada. Depois do congelamento, mudanças no código da avaliação, perguntas ou fontes são detectadas. Não reescrever o snapshot existente para acomodá-las.

A verificação final conferiu os trinta corpora e realizou uma busca técnica nos três índices principais, para os dois métodos, confirmando escopo e integridade. Isso verifica funcionamento e rastreabilidade, não qualidade das respostas finais.
