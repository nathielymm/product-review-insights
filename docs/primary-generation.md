# Geração dos três conjuntos principais

A execução principal v1 foi concluída com as regras congeladas: 14 perguntas × dois métodos × três repetições × três conjuntos, totalizando 252 tentativas. Não houve ajuste de parâmetros, reparação de respostas nem repetição seletiva após observar os resultados.

| Conjunto | Tentativas | Falhas de chamada | Saídas cortadas e com formato inválido | Itens para revisão |
|---|---:|---:|---:|---:|
| Máscaras de cílios | 84 | 0 | 3 | 35 |
| Rotina capilar | 84 | 0 | 3 | 34 |
| Funções variadas | 84 | 0 | 6 | 33 |
| Total | 252 | 0 | 12 | 102 |

As 12 saídas cortadas atingiram o limite de geração e falharam na validação do formato estruturado. Permanecem integralmente nos arquivos de execução, com contexto e estado técnico. As outras 240 passaram pela validação mecânica do formato; isso não comprova fidelidade ou qualidade dos insights.

## Integridade e recursos

A conferência posterior validou perguntas, corpora, índices, parâmetros, código e vínculos com o congelamento. Cada combinação de pergunta, método e repetição aparece exatamente uma vez em seu conjunto. Todos os 252 registros estão vinculados uma única vez aos pacotes de revisão. Os hashes dos três arquivos de respostas constam no resumo agregado ao lado deste documento.

A rotina completa levou aproximadamente 41 minutos e 51 segundos, incluindo preparação local e criação dos pacotes. Esse tempo total não é a latência de uma resposta. Tempos por chamada e contagens de tokens foram registrados para análise posterior. Não houve monitoramento de memória nem enumeração de processos. O servidor local iniciado pela rotina foi encerrado ao final.

## Revisão pendente

Foram preparados 102 itens de revisão, ocultando método, repetição, tempos, scores de recuperação e grupos de clustering. Apenas quadros exatamente iguais — pergunta, resposta, evidências e estado técnico — compartilham uma anotação. Isso evita revisar 150 duplicatas, mas preserva todas as 252 tentativas e suas medições originais. Os itens não constituem 102 amostras independentes.

Nenhuma anotação de qualidade foi preenchida. Cobertura temática, fidelidade, critérios de propostas e controles continuam pendentes; comparações de qualidade permanecem ausentes, sem conclusão de superioridade. A análise de sensibilidade ainda não foi executada.

As respostas, evidências e chaves de revisão permanecem apenas em `results/evaluation-v1/`, ignorado pelo Git. Os pacotes estão em `mascaras-review`, `capilar-review` e `variado-review`; `blind.private.json` contém respostas e evidências, e `annotations.private.json` contém a ficha ainda vazia. A chave que revela os métodos fica separada. Nenhum dado individual foi incluído no commit ou no arquivo de código-fonte.

Próximo passo: revisar os itens com a rubrica congelada e registrar trechos de apoio, sem revelar os métodos durante a anotação. A autorização anterior das referências não preenche automaticamente essas fichas.
