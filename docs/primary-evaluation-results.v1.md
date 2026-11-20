# Resultados da avaliação principal v1

A anotação dos 102 itens únicos foi concluída e vinculada às 252 tentativas originais. Foram julgadas 1.568 unidades de afirmação em seu contexto, incluindo atribuição à família, qualificações e apoio das citações. As 12 saídas cortadas foram mantidas; nenhum experimento foi repetido, reparado ou reconfigurado. As 18 interpretações da amostra e cinco de calibração foram revisadas pela usuária; as demais decisões e a operacionalização numérica são do assistente. Não se trata de referência humana independente.

## Resultado principal

Na anotação v1, o temático apresentou maior fidelidade média nos três casos. A cobertura da referência foi menor no conjunto de máscaras e maior no capilar e no variado. Portanto, não houve ganho consistente de cobertura nem superioridade geral demonstrada. A fidelidade não mede completude: uma resposta pode se apoiar bem em poucos comentários e ainda omitir muitos aspectos.

| Conjunto | Método | Cobertura na recuperação | Cobertura na resposta | Fidelidade | Latência mediana |
|---|---|---:|---:|---:|---:|
| Máscaras | Tradicional | 20,2% | 13,7% | 79,0% | 7,21 s |
| Máscaras | Temático | 12,2% | 6,7% | 84,7% | 6,89 s |
| Capilar | Tradicional | 18,3% | 12,8% | 71,4% | 8,24 s |
| Capilar | Temático | 21,3% | 17,1% | 81,5% | 9,66 s |
| Variado | Tradicional | 9,4% | 3,3% | 75,4% | 6,05 s |
| Variado | Temático | 8,1% | 4,7% | 81,6% | 7,98 s |

Cobertura: média entre famílias elegíveis em cada pergunta, seguida da média das três repetições e das nove perguntas factuais. O denominador são as unidades da referência auditada e não exaustiva: 64 de máscaras, 52 do capilar e 63 do variado. Isso não é a porcentagem de todos os temas que existem no corpus. Qualificações essenciais, contrastes entre pessoas e versões e atribuição à família precisam ser preservados. Aspectos não recuperados e aspectos recuperados mas omitidos são registrados separadamente.

Fidelidade: proporção de unidades de afirmação sustentadas no contexto recuperado, com média das repetições por pergunta e depois das 14 perguntas. Relatos de eficácia e sintomas são avaliados como relatos, não como comprovação técnica ou clínica. As unidades de afirmação não são observações independentes. Latência: mediana do tempo de recuperação mais geração das 42 tentativas por método/conjunto, incluindo saídas inválidas.

## Incerteza das diferenças

Diferença = temático menos tradicional, em pontos percentuais. Os intervalos são os do bootstrap pareado congelado: 2.000 reamostragens de perguntas, semente 42, após média das repetições. São nove perguntas para cobertura e 14 para fidelidade; as perguntas têm dependência temática, portanto os intervalos são exploratórios.

| Conjunto | Diferença de cobertura da resposta [IC 95%] | Diferença de fidelidade [IC 95%] |
|---|---:|---:|
| Máscaras | -7,0 [-18,1; +0,0] | +5,8 [-1,2; +12,4] |
| Capilar | +4,4 [-2,3; +11,3] | +10,1 [+0,6; +21,0] |
| Variado | +1,4 [-2,2; +5,6] | +6,2 [-5,4; +19,2] |

Os intervalos de cobertura incluem zero ou têm zero no limite nos três casos. Para fidelidade, apenas o intervalo do capilar fica inteiramente acima de zero nesta anotação. Isso não estabelece um efeito causal da variedade nem substitui avaliação independente: há um caso por condição, referência parcial e julgamentos assistidos por IA.

## Propostas e controles

Cada critério é binário por resposta e reportado separadamente, conforme a rubrica; não foi criada nota composta. As taxas abaixo são médias das três perguntas de propostas após média das repetições. O julgamento é da resposta inteira: uma violação material pode impedir crédito mesmo quando há uma sugestão útil em outra família. Zero em pertinência não significa ausência de qualquer ideia útil.

| Conjunto | Método | Vínculo com problema/família | Separa relato de proposta | Pertinência à tarefa | Explicita validação/incerteza |
|---|---|---:|---:|---:|---:|
| Máscaras | Tradicional | 66,7% | 66,7% | 0,0% | 66,7% |
| Máscaras | Temático | 33,3% | 100,0% | 0,0% | 66,7% |
| Capilar | Tradicional | 33,3% | 66,7% | 33,3% | 33,3% |
| Capilar | Temático | 66,7% | 66,7% | 33,3% | 66,7% |
| Variado | Tradicional | 100,0% | 66,7% | 33,3% | 33,3% |
| Variado | Temático | 33,3% | 100,0% | 33,3% | 33,3% |

Nos controles, ambos os métodos evitaram garantias ou previsões injustificadas em todas as respostas. O limite pedido foi reconhecido explicitamente em todas as combinações, exceto no tradicional/variado: média de 50% nas duas perguntas de controle. O caso não oferecia garantia de vendas, mas respondia sobre eficácia sem explicitar o limite da previsão comercial. Conforme revisão da usuária, sugestões úteis como hipóteses são permitidas; sua ausência foi registrada qualitativamente, sem acrescentar critério ao controle congelado.

## Citações, contradições e recursos

| Conjunto | Método | Citações com apoio | Contradição | Entrada (tokens) | Saída (tokens) | Formato inválido |
|---|---|---:|---:|---:|---:|---:|
| Máscaras | Tradicional | 77,8% | 1,9% | 61098 | 20135 | 3/42 |
| Máscaras | Temático | 84,7% | 1,0% | 60756 | 17231 | 0/42 |
| Capilar | Tradicional | 70,9% | 6,1% | 60783 | 16887 | 0/42 |
| Capilar | Temático | 82,6% | 3,9% | 63207 | 22927 | 3/42 |
| Variado | Tradicional | 71,9% | 0,0% | 69939 | 18479 | 3/42 |
| Variado | Temático | 82,7% | 0,1% | 68523 | 22864 | 3/42 |

A taxa de apoio das citações usa julgamentos de suporte das passagens associadas, distinguindo falta de citação de citação que não sustenta a afirmação; a média é por pergunta após repetições. Contradição não é sinônimo de falta de suporte. As contagens de tokens são somas reportadas pelo Ollama para as 42 tentativas de cada método/conjunto. Não são custo monetário, energia, memória, tempo de CPU nem medida direta de operações computacionais. Não houve monitoramento de memória ou processos. O temático foi mais rápido na mediana em máscaras e mais lento no capilar e no variado nesta execução local; não extrapolar para outros equipamentos.

## Rastreabilidade e limites da anotação

- Os pacotes cegos, corpora, perguntas, índices, modelo, parâmetros, denominadores, runtime e código congelado passaram nas verificações de integridade. Todos os registros originais estão mapeados exatamente uma vez. As regras e as saídas não foram alteradas para favorecer resultados.
- A análise semântica foi feita pelo assistente sem usar rótulos de método nas fichas. A revisão humana das interpretações foi parcial e acompanhada da interpretação do assistente; não se alega cegamento completo nem anotação independente. Os julgamentos numéricos finais não foram individualmente revisados pela usuária.
- Os candidatos a afirmações foram segmentados por frases e conjunções e julgados no contexto completo da família e sentença. Repetições textuais idênticas na mesma família foram deduplicadas; ressalvas epistêmicas e sugestões de verificação não entram como fatos. Afirmações sobre restrições técnicas e sobre quem relatou algo entram. Fragmentos e afirmações compostas tornam a granularidade uma limitação da fidelidade; os valores dependem dessa operacionalização.
- Há registro de trechos exatos de apoio, rótulos sustentado/contradito/sem suporte, exclusões e um ledger de cobertura para cada unidade/pergunta. Cobertura exige ponto material e qualificações essenciais; não é correspondência lexical. Evidência alternativa da mesma família pôde apoiar unidades já elegíveis sem alterar denominadores.
- As correções humanas sobre adaptação do uso, integridade do lacre, valor percebido e tradução da escova foram preservadas. Nenhuma fonte individual foi versionada. Notas originais e snapshots anteriores continuam disponíveis localmente.
- As comparações só foram liberadas após 102 fichas completas. Recalcular a pontuação e o relatório agregado produziu resultados idênticos. A aprovação humana das interpretações não foi transformada em medida de concordância entre avaliadores.
- A referência é auditada, parcial e orientada a aspectos específicos. Cobertura baixa não equivale a ausência de todo insight útil. A análise de sensibilidade nos subconjuntos ainda não foi executada, e os resultados não sustentam conclusões gerais sobre todas as categorias ou sobre o efeito isolado da variedade.

## Reprodução local

O arquivo `docs/primary-evaluation-results.v1.json` contém apenas agregados, hashes e comparações. As fichas, evidências, decisões, backups e selagem anterior à comparação permanecem sob `results/evaluation-v1/`, ignorado pelo Git.

```sh
.venv/bin/python scripts/report_primary_evaluation.py --output results/evaluation-v1/novo-relatorio-agregado.json
```

O exportador usa `score_study` congelado, valida as entradas e recusa pontuação incompleta ou sobrescrita de relatório. Exige os artefatos privados locais. O ZIP de código-fonte não inclui avaliações, anotações individuais ou modelos.

Próxima etapa: executar a análise de sensibilidade prevista e integrar os achados, limitações e discussão ao texto acadêmico. Nenhuma nova geração é necessária para reproduzir as métricas principais.
