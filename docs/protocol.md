> Estado atual: avaliação integrada e congelamento técnico v1 em docs/evaluation-freeze.md. O custo será descrito por tempos e tokens; memória está fora do escopo.

> Atualização: revisão direcionada concluída; versão atual com 3.843 avaliações em configs/corpus-current.json. Ver docs/final-corpus-qa.md. As 3.846 abaixo descrevem o snapshot anterior à revisão.

# Protocolo experimental atual


O desenho alinhado usa todas as avaliações elegíveis das 15 famílias selecionadas na análise principal. A proposta anterior de limitar a 50 por família foi substituída. A configuração ativa é configs/study-scope.json; a preparação foi executada localmente e aguarda revisão manual final e definição do benchmark.

| Conjunto | Famílias | Avaliações principais |
|---|---:|---:|
| Compacto: máscaras de cílios | 5 | 547 |
| Intermediário: cuidados e ferramentas para cabelo | 5 | 1.408 |
| Variado: funções de diferentes áreas | 5 | 1.891 |
| Total | 15 | 3.846 |

Cada método usa exatamente o mesmo corpus dentro de cada conjunto. As famílias são grupos operacionais por parent_asin, não necessariamente SKUs ou versões idênticas. ASINs dos itens e datas de origem são preservados localmente; não atribuímos características do catálogo atual a todas as avaliações históricas.

Como análise secundária, foram preparados subconjuntos de 20, 40 e 60 avaliações por família: 100, 200 e 300 por conjunto, com sementes 11, 23 e 37. São 27 corpora balanceados. Para cada semente, os subconjuntos menores estão contidos nos maiores. Todos os tamanhos e sementes devem ser reportados; não escolher aquele que favorecer um método. Essa grade é viável nos dados e permite verificar sensibilidade; não representa tamanho ótimo, cálculo de poder ou saturação demonstrada.

O complemento controla volume e participação das famílias, mas não iguala exatamente comprimento, notas ou períodos. Mudanças nos resultados não podem ser atribuídas exclusivamente ao volume. As sementes não constituem conjuntos independentes.

## Elegibilidade e separação

Mantidos os critérios exploratórios: inglês detectado com seed fixa e score mínimo 0,90, texto limpo com 20–200 palavras, nota válida e deduplicação por família e texto normalizado/redigido. O score do detector não é probabilidade calibrada. Não há seleção por tema ou nota. A fonte fornecida tem procedência declarada, sem demonstração de identidade exata com uma distribuição oficial.

Os 90 comentários usados na inspeção temática foram reservados e excluídos dos corpora principais e secundários. A usuária aprovou cinco interpretações; os outros 85 registros não têm aprovação humana registrada. A codificação do assistente não é referência humana independente.

Desenvolvimento usa cinco outras famílias, sem sobreposição com as 15 da avaliação: 625 avaliações, além de nove subconjuntos para desenvolvimento. Os conjuntos de avaliação foram explorados para escolher o recorte; essa inspeção deve ser declarada, sem apresentá-los como teste inteiramente intocado.

Há uma avaliação deduplicada com notas conflitantes no conjunto intermediário. A regra determinística preexistente preserva a menor nota e sinaliza o conflito; isso pode afetar estatísticas de notas. Textos passam por redação heurística, sem garantia de anonimização completa. Revisão de privacidade, pertinência, incentivos e versões continua pendente.

## Evidências de preparação

Foram gerados 40 pares corpus/manifesto: três principais, 27 secundários, um de desenvolvimento e nove curvas de desenvolvimento. Manifestos registram hashes da fonte, pools, exclusão da auditoria, configuração e corpus, identidades, contagens, notas e datas agregadas. A preparação exige destino novo e falha em caso de divergência de hashes ou falta de avaliações. Dados, modelos e resultados individuais permanecem fora do Git.

Passaram 30 testes automatizados. Um índice real de desenvolvimento com 625 avaliações, 627 trechos e embeddings de 384 dimensões recuperou apenas famílias permitidas nos dois métodos. Uma solicitação para outro conjunto foi rejeitada antes da geração. Não houve chamadas ao Ollama nessa verificação nem cálculo de qualidade das respostas. A configuração de 12 grupos desse teste não está selecionada como hiperparâmetro final.

## Antes da avaliação final

Revisar qualidade e versões; fechar as perguntas e referências por conjunto; ajustar parâmetros somente no desenvolvimento e congelar configurações e hashes. A referência de cada subconjunto deve corresponder às evidências que ele contém: distinguir disponibilidade de evidência de cobertura da resposta condicionada a essa disponibilidade. Não reutilizar automaticamente o denominador temático do corpus completo.

Avaliar cobertura temática, sustentação de afirmações nas evidências, abstenção, latência e recursos locais, com orçamento de contexto e geração comparável entre métodos. Registrar tempos de preparação/indexação separadamente da consulta, hardware, contagem de tokens e digest do modelo, sem coleta de memória ou listagem de processos. Não há resultados finais de cobertura, fidelidade ou superioridade.

Um conjunto por condição permite três estudos de caso, sem isolar causalmente o efeito da variedade. Os dez temas amplos observados nos três conjuntos não demonstram uma ordem crescente de diversidade temática.

A organização em corpus, perguntas e julgamentos é compatível com [TREC](https://trec.nist.gov/howto.html) e [BEIR](https://github.com/beir-cellar/beir); a avaliação de RAG exige critérios explícitos, como discutido em [RAGBench](https://arxiv.org/abs/2407.11005). Usar o corpus elegível completo com análise secundária balanceada é uma escolha deste projeto, não uma quantidade universal prescrita por essas fontes.

## Anotação e execução

As 16 perguntas em configs/questions.eval.draft.json permanecem em rascunho. Preparar julgamentos de referência antes da avaliação, vinculados ao conjunto e corpus. Ocultar o método na revisão das respostas, manter a chave privada e registrar desacordos e critérios. Citações existentes não demonstram sustentação sem leitura da evidência. Comparar métodos de forma pareada por pergunta; documentos não são réplicas independentes.

O runner exige --cohort para perguntas com scope_required, rejeita o piloto global e conjuntos incompatíveis antes de gerar respostas. Esse controle não substitui a revisão semântica das perguntas. Não executar avaliação final antes de congelar benchmark, parâmetros e referências.
