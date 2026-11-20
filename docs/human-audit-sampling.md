# Amostra de revisão humana parcial

Foram sorteados 18 itens únicos, seis por conjunto: três perguntas factuais distintas, duas de propostas distintas e uma de controle. Os dois tipos de controle estão representados entre os conjuntos.

Semente: 20261116. Sorteio em duas etapas: pergunta uniforme sem reposição dentro do tipo e, depois, item uniforme dentro da pergunta. Controles alternados entre conjuntos após sorteio do primeiro tipo. O script local preserva ordem, semente, IDs selecionados e hashes dos pacotes de origem, permitindo reproduzir a seleção. Não foram consultadas as chaves dos métodos, as notas de qualidade nem o estado técnico para selecionar os itens. Não haverá substituição por desempenho observado.

Os cinco itens de máscaras já aprovados foram separados como calibração. O sexto, já apresentado e ainda não aprovado, também foi excluído do sorteio para evitar exposição prévia. Isso deixa 96 candidatos não apresentados, dos quais 18 foram selecionados. Os demais poderão ser anotados pelo assistente; casos ambíguos adicionais serão identificados separadamente da amostra.

A distribuição igual por conjunto/tipo é deliberada e não proporcional à população de itens. Itens de perguntas distintas têm probabilidades de inclusão diferentes; não usar concordância bruta desta amostra como estimativa não ponderada de toda a avaliação. O tamanho é um compromisso de carga de revisão, sem margem de erro garantida. As revisões não são independentes: a usuária recebe uma interpretação assistida por IA. Não se trata de referência humana integral nem independente. As anotações originais e correções serão preservadas.

A seleção é uma mudança documentada no plano de revisão humana, posterior à geração. Não modifica perguntas, corpora, modelos, respostas ou regras de pontuação congeladas. Comparações finais continuam pendentes.

O registro individual e o script ficam em `results/evaluation-v1/human-audit/`, fora do Git. O primeiro item é H01; sua interpretação inicial foi registrada antes da revisão humana. Os 18 itens tiveram suas interpretações qualitativas revisadas e aprovadas, com correções preservadas separadamente dos rascunhos iniciais. Isso não equivale a 18 fichas de pontuação formal completas. Três controles já receberam os critérios booleanos previstos na rubrica; a decomposição das afirmações e a cobertura por unidade ainda estão pendentes. Ver docs/human-audit-progress.json.
