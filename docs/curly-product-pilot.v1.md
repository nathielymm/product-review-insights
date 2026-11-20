# Piloto Curly Co.: temas dentro de um produto

Foram usadas 804 avaliações elegíveis do difusor Curly Co. (B019GBG0IE), segmentadas em 805 trechos. O caso passa a ser desenvolvimento: seus resultados poderão orientar ajustes e não devem ser tratados como teste final independente.

## Comparação preparada

Os agrupamentos foram recalculados exclusivamente dentro do produto. Quatro grupos exploratórios foram fixados antes das respostas, sem seleção por desempenho: 251, 191, 182 e 181 trechos. A inspeção de termos e três exemplos representativos por grupo sugeriu sobreposição entre encaixe/portabilidade, resultado nos cachos/tempo de secagem e colapso no uso. São agrupamentos vetoriais com interpretação inicial, não quatro temas semanticamente validados ou exclusivos.

O tradicional selecionou por similaridade; o temático diversificou grupos entre os mesmos 80 candidatos e completou por similaridade. Ambos tiveram até oito trechos, 12.000 caracteres de contexto, janela de 8.192 tokens, limite de 1.536 tokens de saída, temperatura 0 e semente 42, com Gemma 3 4B local. Perguntas de geração em português e equivalentes de recuperação em inglês foram fixados e compartilhados, considerando o encoder MiniLM existente. Não houve expansão por aspectos ou busca adicional apenas para um método.

O contrato comum pediu achados específicos, preservação de condições e experiências, propostas como hipóteses e resposta em português. Não foram modificados fontes, índices, prompts ou resultados necessários aos experimentos congelados anteriores. A interface continua separada e não usa automaticamente estes novos grupos.

## Perguntas

1. Quais problemas específicos são relatados, em quais condições e que experiências divergentes aparecem?
2. Que melhorias poderiam ser investigadas a partir desses problemas, quais qualidades deveriam ser preservadas e o que precisaria ser validado?

## Resultados operacionais

Uma tentativa por pergunta/método, quatro no total; nenhuma falha, formato inválido ou corte. A validade estrutural não garante fidelidade semântica.

| Pergunta | Método | Avaliações incluídas | Avaliações citadas | Grupos no contexto | Achados estruturados | Tempo |
|---|---|---:|---:|---:|---:|---:|
| P01 | Tradicional | 8 | 7 | 2 | 3 | 7.30 s |
| P01 | Temático | 8 | 8 | 2 | 3 | 7.10 s |
| P02 | Tradicional | 8 | 8 | 1 | 2 | 5.74 s |
| P02 | Temático | 8 | 5 | 2 | 1 | 4.42 s |

As contagens de avaliações citadas identificam referências, sem medir se todas sustentam as afirmações. Achados estruturados podem conter várias afirmações. A primeira chamada inclui carregamento do modelo; ordem fixa e uma execução impedem concluir vantagem estável de latência. Tempos de preparação são separados dos tempos da tabela. Tokens e hashes estão no JSON agregado.

## O que o piloto revelou

Na primeira pergunta, os métodos receberam os mesmos oito trechos, em ordem diferente. Ambos abordaram desempenho, colapso e durabilidade, mas ainda combinaram relatos distintos. Na leitura do assistente, o tradicional confundiu prazos e apoios de experiências separadas; o temático preservou melhor alguns contrastes, mas também perdeu limites de atribuição. Diferenças de texto não demonstram benefício de recuperar mais fontes: a composição dos contextos era idêntica.

Na segunda pergunta, sete das oito fontes eram comuns. O tradicional propôs investigar material/fixação, uma hipótese vinculada aos problemas, mas acrescentou explicação causal sem evidência. O temático citou cinco avaliações favoráveis e não propôs melhorias, embora tivesse recebido reclamações de colapso, quebra e material. Assim, uma parte importante da falha ocorreu no aproveitamento das evidências pelo gerador, não somente na sua disponibilidade.

A seleção temática também teve pouco espaço para diversificar: os 80 candidatos continham apenas dois dos quatro grupos locais. Na primeira pergunta eram 59 de um grupo e 21 do outro; na segunda, 60 e 20. Os outros grupos existiam no índice, mas não estavam no conjunto de candidatos dessas perguntas. Isso não significa ausência dos respectivos assuntos: agrupamentos se sobrepõem e um mesmo aspecto aparece em mais de um grupo. O método não pode selecionar grupos fora do seu conjunto de candidatos.

## Conclusão de desenvolvimento

A execução confirmou isolamento de produto e agrupamentos locais, mas ainda não demonstrou a profundidade e a fidelidade desejadas. Há problemas a investigar tanto na concentração dos candidatos para perguntas amplas quanto na síntese e atribuição das evidências. Não há vencedor estabelecido e não será ampliada automaticamente a avaliação com base neste resultado.

A próxima iteração deve separar verificações: primeiro conferir recuperação por aspectos explícitos da pergunta e redundância, com regras comuns aos dois métodos; depois conferir achados menores e apoio por fonte na geração. Qualquer mudança deve ter nova configuração e destino, mantendo estas quatro respostas, inclusive as falhas semânticas. Não presumir que aumentar trechos ou mudar o número de grupos resolverá o problema.

## Limites e reprodução

A conferência foi qualitativa, feita pelo assistente com os métodos visíveis e leitura das fontes efetivamente incluídas. Não houve referência exaustiva, anotação independente, taxa numérica de profundidade ou teste estatístico. O agrupamento e o orçamento ainda são exploratórios. Datas/versões não são inferidas por sentimento, e sugestões do consumidor não são tratadas como causalidade comprovada.

A suíte de software passou com 68 testes, incluindo barreiras de identidade e de sobrescrita; isso não valida a qualidade dos achados. Dados, exemplos, prompts completos, respostas brutas e conferência individual permanecem em diretórios ignorados pelo Git.

Com os artefatos locais, configs/curly-product-pilot.v1.json e scripts/run_product_pilot.py documentam a execução. Os comandos `--prepare` e `--run` recusam destinos existentes. Para repetir, copiar a configuração para novos caminhos de índice e resultados; não sobrescrever os atuais. Mesmo com semente fixa, não se garante igualdade textual de novas gerações.

Para reproduzir somente os agregados, sem nova chamada ao modelo:

```sh
.venv/bin/python scripts/report_product_pilot.py --output results/product-pilot/curly-v1/novos-agregados.json
```

A exportação dos agregados desta execução foi reproduzida com igualdade byte a byte. Essa igualdade não mede correção semântica.
