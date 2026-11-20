# Conclusão da revisão dos corpora

A revisão direcionada foi concluída. A usuária revisou 20 comentários, cobrindo as 15 famílias; isso não constitui revisão humana de todas as avaliações nem referência independente para medir o RAG.

A triagem automatizada percorreu as 3.846 avaliações principais e as 625 de desenvolvimento. Foram inspecionados os casos sinalizados de uso em animais, possível incompatibilidade, contato, assinatura e candidatos a menção de incentivo. As regras são heurísticas, com falsos positivos e possíveis omissões; não demonstram anonimização ou correção completa do corpus.

## Decisões aplicadas

- Excluídos três comentários exclusivamente sobre uso em animais: F008, aprovado pela usuária, e dois casos adicionais da mesma natureza, identificados pelo assistente sob o critério aprovado.
- Mantidos relatos que descrevem experiência humana mesmo quando também mencionam uso em animais. Não usar os resultados em animais para sustentar benefícios humanos.
- Removida uma assinatura pessoal residual. O ID de origem foi preservado, e o conteúdo transformado recebeu novo checksum.
- Mantidos os candidatos a menção de amostras, descontos ou produtos gratuitos. Os 72 alertas principais incluem falsos positivos, negações, reposição de produto e referências a terceiros; não são 72 incentivos confirmados nem evidência de fraude.
- Os seis alertas de possível produto incompatível eram compatíveis com relatos sobre o produto e comparações contextuais; foram mantidos. Não foram encontrados contatos pelos padrões utilizados, o que não garante ausência de dados pessoais.

## Corpus atual

| Conjunto | Avaliações |
|---|---:|
| Compacto — máscaras de cílios | 547 |
| Intermediário — rotina capilar | 1.405 |
| Variado — funções de diferentes áreas | 1.891 |
| Total principal | 3.843 |

Desenvolvimento permanece com 625 avaliações. Os 27 corpora de sensibilidade continuam com 100, 200 e 300 avaliações por conjunto, nas três sementes, e foram reconstruídos após as exclusões. A nova versão é data/processed/study-v2-qa-final; a anterior foi preservada. configs/corpus-current.json identifica a versão atual sem modificar a configuração histórica usada na primeira preparação. Os índices antigos não representam automaticamente esta versão.

## Verificação e reprodução

Passaram 31 testes. Foram conferidos os 40 pares corpus/manifesto, seus hashes, a ausência das três exclusões e dos 90 comentários reservados e o aninhamento dos subconjuntos. Dados, relatórios por registro e textos permanecem fora do Git; o resumo público é docs/final-corpus-qa-summary.json.

Para reproduzir a partir do snapshot local original, usando destinos novos:

```sh
.venv/bin/python scripts/finalize_corpus_qa.py --source data/processed/study-v1 --output data/processed/study-v2-qa-final --report results/final-corpus-qa-v2
```

O comando falha se o destino existir. Configuração das decisões: configs/corpus-qa-decisions.json. Manifestos registram hashes do corpus de origem, decisões e script. Houve uma versão intermediária local de preparação, preservada; somente o caminho indicado em configs/corpus-current.json é a versão atual.

A etapa de revisão direcionada dos dados está encerrada. Ainda precisamos fechar perguntas, referência de avaliação e parâmetros escolhidos no desenvolvimento antes de executar a comparação final. Não há resultados finais de cobertura, fidelidade ou superioridade de método.
