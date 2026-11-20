# Seleção operacional no desenvolvimento

Foi concluída uma seleção operacional de parâmetros usando somente as cinco famílias separadas de desenvolvimento: 625 avaliações e 627 trechos. As respostas e referências de avaliação final não foram usadas para escolher parâmetros. O snapshot atual está indicado em configs/development-current.json.

## Configuração selecionada para a próxima etapa

| Parâmetro | Escolha |
|---|---|
| Modelo | Gemma 3 4B, local via Ollama |
| Embeddings | Snapshot local do MiniLM já usado no projeto |
| Grupos semânticos | 6 |
| Trechos por pergunta | Até 8 |
| Candidatos examinados | Até 80 |
| Orçamento do contexto | 12.000 caracteres |
| Janela do modelo | 8.192 tokens |
| Limite da resposta | 1.536 tokens |
| Temperatura / seed | 0 / 42 |
| Saída | JSON por família, com observação, proposta, incerteza e citações separadas |

Os dois métodos usam a mesma configuração e o mesmo contrato de geração. Muda a seleção dos trechos. Os limites não obrigam o modelo a preencher todos os grupos: arrays vazios permitem ausência de achados relevantes.

## Critérios e evidências da escolha

Foram comparados 6, 12 e 20 grupos, com três sementes, usando os mesmos vetores do corpus de desenvolvimento. Seis grupos tiveram a maior média de silhouette de cosseno (0,1953) e maior estabilidade média entre sementes (ARI 0,7337). Doze tiveram silhouette média 0,1104; vinte, 0,0840, incluindo grupo com um único trecho. Esses números são diagnósticos geométricos, não qualidade de temas ou de respostas.

A inspeção dos descritores mostrou influência forte do tipo de produto: pincéis, desodorantes, condicionador e esmaltes, além de diferenças de cheiro e cor. Não apresentar os seis grupos como seis temas humanos validados. Uma possível melhora da recuperação pode envolver redistribuição de famílias; o experimento não isola isso como efeito causal exclusivamente temático.

Os testes de empacotamento compararam 6, 8 e 12 trechos nas seis perguntas de desenvolvimento, para os dois métodos. Todos cabiam em 12.000 caracteres. Entretanto, caber no contexto não foi suficiente para obter respostas operacionalmente estáveis com doze trechos. Foram observados formato inválido de citações, mistura de famílias e respostas estruturadas cortadas em tentativas intermediárias.

A revisão reduziu o número de trechos para oito e adotou campos separados por família. Como as mudanças foram feitas conjuntamente, não atribuir a melhoria de formato isoladamente à redução de contexto. O replay das seis perguntas × dois métodos confirmou que os oito trechos cabem integralmente no orçamento atual.

## Teste local de geração

Foram preservadas seis iterações de desenvolvimento, totalizando 36 respostas e seis aquecimentos. A última usa três perguntas: experiências negativas de cheiro, propostas de melhoria e limites sobre aumento de vendas, cada uma respondida pelos dois métodos.

As seis respostas da última rodada passaram nas verificações mecânicas: resposta não vazia, finalização sem corte, contexto integral, IDs válidos, contrato estruturado válido e contagem de tokens dentro da janela. Isso é um teste pequeno e adaptativo de desenvolvimento, não validação independente de qualidade nem comparação final dos métodos.

O contrato agrupa evidências por família e separa citações de texto. A apresentação resolve cabeçalhos pelos metadados das fontes escolhidas; não corrige fatos. A validade dos IDs ou do cabeçalho não demonstra que a observação é sustentada pelo comentário. Respostas brutas, erros de validação e versões anteriores permanecem locais para auditoria. Não há reparo factual ou descarte silencioso de falhas.

O recurso de saída estruturada é documentado pelo [Ollama](https://docs.ollama.com/capabilities/structured-outputs). A implementação valida novamente a resposta recebida, pois formato solicitado não substitui validação ou avaliação semântica.

## Limitações que continuam presentes

A leitura qualitativa das seis respostas identificou exemplos de associação entre observação e citação sem suporte suficiente, sugestão inferida apresentada como se fosse pedido do consumidor e propostas sem problema documentado. Esses erros ficaram registrados: serão relevantes à avaliação de fidelidade e pertinência, não apagados por uma nota de formato válida.

Não houve anotação exaustiva de afirmações nem cálculo de cobertura ou fidelidade final. Não há conclusão de superioridade. Os tempos do pequeno piloto são operacionais, com aquecimento e cache, e não substituem o protocolo final de latência/custo.

## Reprodução e estado

Configurações: configs/development-selection-plan.json registra o plano atual. Os planos exploratórios foram preservados no histórico privado de desenvolvimento. O plano atual incorpora automaticamente o limite de oito trechos selecionado no desenvolvimento; a reprodução confirmou configuração, índice, clusters, encoder e corpus idênticos aos testados. A configuração selecionada está em configs/experiment.development-selected.json; os relatórios agregados estão em docs/development-selection-summary.json, docs/development-generation-probe-summary.json e docs/development-parameter-selection.json. O digest do modelo está no último relatório, conferido antes e depois da rodada.

Para novas execuções, usar destinos novos:

```sh
.venv/bin/python scripts/select_development_parameters.py --plan configs/development-selection-plan.json --output results/development-selection/novo --artifact artifacts/development-selection/novo
.venv/bin/python scripts/probe_development_generation.py --plan configs/development-selection-plan.json --index artifacts/development-selection/novo --output results/development-generation/novo
```

O servidor deve usar somente loopback, modelo já baixado e nuvem desativada, conforme docs/reproduction.md. A execução local exigiu permissão de conexão fora do sandbox; não houve envio de avaliações a serviços externos. Arquivos individuais ficam fora do Git. Ao terminar, o modelo foi descarregado e apenas o servidor iniciado para o piloto foi encerrado.

Os 48 testes de software passaram, incluindo bloqueio de corpora de avaliação nesta seleção, separação de famílias com a mesma função, rejeição de citações de outra família, preservação de saída inválida e contratos distintos para saída livre e estruturada.

A seleção operacional está pronta para preparar o congelamento final e integrar a anotação por unidades. Os denominadores/referências elegíveis nos subconjuntos e as configurações finais ainda precisam ser fixados antes dos experimentos de avaliação. Nenhuma resposta do corpus final foi gerada nesta etapa.

Após a rodada bem-sucedida, houve apenas remoção de espaço em branco no fim de uma linha do gerador. O relatório registra separadamente o hash testado e o atual; a igualdade do código normalizado foi verificada. Os artefatos reconstruídos pelo plano atual coincidem com os testados.
