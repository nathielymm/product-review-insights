# Análise de sensibilidade v1

Estado: concluída a grade de 27 cenários, com 756 tentativas e 756 fichas anotadas pelo assistente, somando 11.876 unidades de afirmação. As regras congeladas foram preservadas. A comparação não mostra vantagem consistente do método temático.

## Desenho preservado

São 27 cenários: três conjuntos, 20/40/60 avaliações por família e sementes 11/23/37. Cada cenário contém cinco famílias, 14 perguntas, dois métodos e uma repetição: 28 tentativas. Os menores subconjuntos estão contidos nos maiores para a mesma semente. Todos os cenários devem ser mantidos; não há seleção posterior de sementes ou tamanhos.

A configuração é a do congelamento v1: Gemma 3 4B local, embeddings MiniLM, FAISS, seis agrupamentos, oito passagens de contexto, mesmo limite de candidatos e orçamento de geração. Corpus, perguntas, referência, runtime, modelo e código são verificados por hashes. A análise principal permanece um resultado separado.

## Cobertura e denominadores

A referência auditada é parcial. Sua elegibilidade em cada subconjunto depende dos apoios conhecidos presentes nele. Há 58 combinações de pergunta/subconjunto sem apoio conhecido: nesses casos a cobertura é indisponível, não zero. Isso não demonstra ausência do tema no corpus. Evidência alternativa da mesma família pode apoiar unidades já elegíveis; não houve ampliação silenciosa dos denominadores.

A pontuação exige correspondência semântica com o aspecto e suas qualificações essenciais. Famílias, pessoas, versões, comparações e contexto de uso precisam ser preservados. Cobertura na recuperação e na resposta são distintas; recuperar um comentário não significa que o modelo incorporou o ponto à resposta.

## Anotação e interpretação

Os julgamentos são do assistente, aplicando a rubrica congelada e as convenções de interpretação da auditoria humana principal. Os novos itens de sensibilidade não têm pontuação humana independente. A extração por frases e conjunções apenas organiza candidatos; não determina o julgamento semântico. Repetições textuais na mesma família são deduplicadas. Ressalvas epistêmicas e sugestões de verificação não são fatos; afirmações técnicas e atribuições ao que uma pessoa relatou entram no denominador de fidelidade. A granularidade das unidades limita a interpretação da taxa.

As fichas não mostram o método. As anotações e suas versões são preservadas antes de liberar comparações. A extração de todas as observações em JSON inválido foi completada nos dois primeiros cenários antes dessa liberação, mantendo os arquivos e selos anteriores. Também foi corrigida, antes da comparação, a normalização de identificadores com zero à esquerda no código auxiliar de apoio das citações; todas as fichas afetadas foram revalidadas, com versões anteriores preservadas. Também se harmonizou a exigência de “assobio ou barulho alto”, sem creditar ruído genérico, em duas fichas antes da comparação, preservando as versões anteriores. Essas conferências não modificaram respostas do modelo nem a elegibilidade das referências. Um selo global foi gravado após validar todas as fichas e antes de exportar os resultados comparativos.

As métricas são reportadas por cenário e por conjunto/tamanho. Médias e amplitudes entre três sementes são descritivas; não são intervalos de confiança. Os intervalos por cenário usam o bootstrap pareado já congelado, com perguntas dependentes e uma única repetição. Não se tratam as sementes, tamanhos aninhados ou unidades de afirmação como observações independentes.

Propostas têm quatro critérios binários separados; controles têm dois. Não há nota composta. Sugestões úteis podem ser hipóteses mesmo sem dados de vendas, mas não autorizam previsões causais ou garantias universais.

## Integridade e recursos

Saídas inválidas, cortes e erros são preservados. Não há nova tentativa automática para obter uma resposta melhor. Antes da geração, uma tentativa de preparação com variáveis de modo offline alterou a serialização do tokenizador e foi rejeitada pela verificação de hash. O artefato rejeitado foi preservado; a preparação foi refeita em destinos novos com o ambiente original e os mesmos arquivos locais, sem alterar o congelamento. Nenhuma resposta havia sido gerada nessa tentativa de preparação.

Os recursos medidos são tempos de parede e tokens informados pelo Ollama, incluindo tentativas inválidas. Tokens não equivalem a dinheiro, energia, memória ou operações computacionais. Não houve listagem de processos ou monitoramento de memória/CPU. Anotação por leitura/gravação de arquivos e testes leves do exportador ocorreram durante a geração; a carga compartilhada e a ordem fixa limitam comparações de latência nesta máquina.

## Resultados medidos

Cada linha abaixo resume três sementes. Coberturas e fidelidade são médias das médias por pergunta de cada cenário, com pesos iguais entre sementes. A cobertura usa média entre famílias elegíveis; a fidelidade usa a proporção de afirmações sustentadas dentro de cada resposta. Cobertura indisponível é excluída da média e continua explícita por cenário no JSON. A latência é a mediana das 42 tentativas do método no grupo, incluindo falhas e cortes; não é a média de medianas.

| Conjunto | Avaliações/família | Método | Cobertura recuperação | Cobertura resposta | Fidelidade | Mediana tempo |
|---|---:|---|---:|---:|---:|---:|
| Máscaras | 20 | Tradicional | 34.1% | 28.7% | 83.3% | 7.12 s |
| Máscaras | 20 | Temático | 44.0% | 28.2% | 83.0% | 7.23 s |
| Máscaras | 40 | Tradicional | 17.0% | 8.9% | 88.1% | 8.00 s |
| Máscaras | 40 | Temático | 19.1% | 11.7% | 86.6% | 8.12 s |
| Máscaras | 60 | Tradicional | 20.1% | 15.2% | 88.0% | 7.33 s |
| Máscaras | 60 | Temático | 18.6% | 10.9% | 87.0% | 7.49 s |
| Capilar | 20 | Tradicional | 30.0% | 26.7% | 90.9% | 7.48 s |
| Capilar | 20 | Temático | 30.0% | 26.7% | 88.6% | 8.12 s |
| Capilar | 40 | Tradicional | 23.4% | 18.3% | 90.0% | 7.55 s |
| Capilar | 40 | Temático | 13.1% | 2.8% | 90.2% | 8.52 s |
| Capilar | 60 | Tradicional | 20.1% | 12.5% | 91.3% | 8.38 s |
| Capilar | 60 | Temático | 20.8% | 14.6% | 92.6% | 8.95 s |
| Variado | 20 | Tradicional | 10.0% | 10.0% | 82.4% | 7.90 s |
| Variado | 20 | Temático | 24.4% | 13.3% | 83.9% | 9.51 s |
| Variado | 40 | Tradicional | 14.4% | 14.4% | 83.3% | 7.88 s |
| Variado | 40 | Temático | 12.7% | 10.8% | 87.6% | 8.66 s |
| Variado | 60 | Tradicional | 13.4% | 6.5% | 85.2% | 8.82 s |
| Variado | 60 | Temático | 16.7% | 10.0% | 84.6% | 10.49 s |

As diferenças abaixo são temático menos tradicional, em pontos percentuais (pp). A amplitude entre sementes é descritiva. Os intervalos bootstrap por cenário e os valores por pergunta estão nos agregados, sem transformar as três sementes em um teste independente.

| Conjunto | n/família | Δ cobertura resposta: média [mín.; máx.] pp | Δ fidelidade: média [mín.; máx.] pp | Unidades elegíveis: mín.–máx. |
|---|---:|---:|---:|---:|
| Máscaras | 20 | -0.46 [-12.50; +11.11] | -0.24 [-4.34; +5.92] | 8–16 |
| Máscaras | 40 | +2.84 [-2.78; +5.93] | -1.46 [-5.04; +1.84] | 22–36 |
| Máscaras | 60 | -4.31 [-7.78; -1.11] | -1.04 [-7.84; +4.16] | 42–46 |
| Capilar | 20 | +0.00 [+0.00; +0.00] | -2.35 [-4.25; -0.38] | 4–6 |
| Capilar | 40 | -15.48 [-21.43; -8.33] | +0.14 [-4.21; +4.39] | 9–10 |
| Capilar | 60 | +2.08 [-8.33; +14.58] | +1.38 [-1.87; +6.59] | 13–15 |
| Variado | 20 | +3.33 [+0.00; +10.00] | +1.51 [-2.91; +9.84] | 2–9 |
| Variado | 40 | -3.59 [-16.67; +3.12] | +4.30 [-0.24; +7.46] | 7–17 |
| Variado | 60 | +3.55 [-5.56; +12.50] | -0.60 [-2.95; +2.35] | 14–25 |

A cobertura da resposta favoreceu o temático em quatro médias de grupo, o tradicional em quatro e empatou em uma. Mesmo quando a recuperação melhora, a resposta pode não incorporar o tema: em máscaras/n20, a recuperação aumenta 9,88 pp, mas a cobertura da resposta cai 0,46 pp. Capilar/n40 favorece o tradicional nas três sementes para cobertura da resposta; máscaras/n60 também. Não há progressão monotônica ou vantagem geral.

A maior fidelidade do temático observada na análise principal não se repetiu de forma estável: na sensibilidade, a diferença média é positiva em quatro dos nove grupos e negativa em cinco. Em capilar/n20, é negativa nas três sementes. A referência parcial, os contextos diferentes e a anotação assistida impedem interpretar a diferença entre etapas como efeito isolado do volume. Ampliar o corpus também amplia e modifica o denominador elegível; por isso, uma queda de cobertura entre tamanhos não demonstra piora absoluta do sistema.

## Propostas, controles e operações

Os critérios de propostas abaixo são médias descritivas com pesos iguais para as três perguntas, sementes e grupos; cada método teve 81 respostas a propostas. Não há pontuação composta nem teste de superioridade.

| Critério de proposta | Tradicional | Temático |
|---|---:|---:|
| Vínculo com problema e família sustentados | 63.0% | 58.0% |
| Proposta distinguida do relato | 75.3% | 79.0% |
| Pertinência à tarefa | 33.3% | 33.3% |
| Incertezas e validação explícitas | 70.4% | 70.4% |

Nos 54 controles por método, o limite epistêmico foi reconhecido em 100% no tradicional e 98,1% no temático; ausência de garantia ou previsão causal injustificada teve 100% em ambos. Esses critérios avaliam a resposta à pergunta de controle, não certificam segurança de produtos ou ausência de erros factuais no restante do texto.

| Operação, todas as tentativas | Tradicional | Temático |
|---|---:|---:|
| Tentativas | 378 | 378 |
| Falhas de chamada | 1 | 0 |
| Formato inválido | 24 | 18 |
| Cortes pelo limite | 19 | 15 |
| Tokens de entrada informados | 564805 | 565257 |
| Tokens de saída informados | 182636 | 190270 |

A única falha foi HTTP 500 em capilar/n40/semente11/Q09 no tradicional, mantida como resposta vazia: tarefa de proposta não atendida e fidelidade indisponível por ausência de afirmações, sem atribuir 100% artificial. Tokens dessa chamada não foram informados; os totais acima somam apenas valores observados. Formato inválido, corte e erro podem se sobrepor e não devem ser somados como tentativas distintas. As 34 saídas cortadas e as demais inválidas foram anotadas a partir do texto efetivamente disponível, sem reparar ou regenerar respostas.

O temático foi mais lento nas medianas dos nove grupos. Isso não estabelece custo universal: tempo local depende de comprimento da resposta, aquecimento, execução em ordem fixa e carga compartilhada. Houve um intervalo no progresso global cuja causa não foi estabelecida; os tempos originais por chamada foram preservados, sem ajuste posterior. Não foram medidos memória, CPU, energia ou custo monetário. Tempos de construção dos 27 índices e tokens/latências por cenário estão no JSON.

## Conclusão e limites

O enriquecimento por diversidade temática, com a configuração congelada, não demonstrou benefício robusto sobre similaridade tradicional nesta grade. Há ganhos localizados e perdas, e melhor recuperação de aspectos nem sempre se converte em melhor resposta. A pertinência das propostas continua baixa em ambos, indicando espaço para melhorar a ligação entre a pergunta, o problema documentado e uma hipótese de melhoria verificável.

A conclusão se limita a estas famílias, referência parcial, modelo e orçamento de contexto. Há uma repetição por cenário, três sementes, perguntas dependentes e tamanhos aninhados. A avaliação semântica de sensibilidade foi feita pelo assistente com convenções humanas anteriores, sem nova revisão humana independente; a granularidade das afirmações e possíveis erros de anotação limitam a força dos resultados. Não se demonstra efeito causal da variedade nem superioridade geral de uma arquitetura. Os resultados principais permanecem separados e preservados.

A exportação foi reproduzida em novo arquivo com igualdade byte a byte. A suíte de software passou com 57 testes; esses testes verificam o cálculo e suas barreiras, não validam semanticamente os insights. O relatório público contém agregados; os textos e fichas individuais permanecem privados.

## Reprodução dos agregados

Com os artefatos privados locais completos, usar um destino novo:

```sh
.venv/bin/python scripts/report_sensitivity_evaluation.py --output results/sensitivity-v1-execution/reproducao-agregada.json
```

O exportador valida o congelamento e as anotações, recusa execução incompleta e não sobrescreve relatórios. Dados, modelos, respostas, evidências, chaves e fichas individuais permanecem locais e ignorados pelo Git. Nenhuma publicação no GitHub está autorizada.
