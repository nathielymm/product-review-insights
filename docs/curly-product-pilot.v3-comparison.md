# Curly Co.: terceira rodada com geração simplificada

Estado: quatro novas respostas em português, com JSON válido e fontes originais apresentadas pelo sistema. Rodadas anteriores preservadas. Esta é uma iteração de desenvolvimento; os erros semânticos encontrados impedem declarar configuração final aprovada ou superioridade de um método.

## Mudança isolada na geração

A recuperação da segunda rodada foi mantida: mesmo corpus de 804 avaliações/805 trechos, índice, quatro grupos locais, consultas por aspectos, fusão e deduplicação, além dos mesmos candidatos e trechos na mesma ordem para cada pergunta/método. O executor exige igualdade de IDs e textos com a rodada anterior antes de chamar o modelo. Modelo/digest, runtime, até oito trechos, contexto de 12.000 caracteres, janela de 8.192 tokens, teto de 1.536 tokens de saída e temperatura 0/semente 42 permaneceram iguais.

A geração mudou como um pacote: prompt integralmente em português, nomes dos campos em português e contrato reduzido a fonte, relato, melhoria e validação, com limite geral. Foram removidos citação copiada, classificação de problema/qualidade, aspecto e condição como campos separados. A condição, quando existir, deve ser preservada no relato. O limite continuou sendo seis achados, com um identificador de fonte por achado. A primeira pergunta não permite propostas no campo melhoria.

O modelo não produz o texto do painel de fontes. Após validar os identificadores, o sistema busca os trechos originais incluídos no contexto e os apresenta literalmente, sem tradução, correção ou resumo. Vários achados ligados à mesma avaliação compartilham a fonte, sem contá-la duas vezes. Esse mecanismo impede que o painel apresente uma citação inventada pelo modelo; não garante que a interpretação esteja sustentada pela avaliação escolhida.

Não houve novas tentativas, tradução pós-geração, reparo de resposta ou troca de fontes. Uma tentativa por pergunta/método. Como prompt e esquema mudaram juntos, a comparação não identifica o efeito isolado da retirada da cópia literal.

## Comparação operacional com a segunda rodada

| Pergunta | Método | Rodada 2: contrato / idioma das observações | Rodada 3: contrato / idioma das observações | Fontes incluídas na rodada 3 | Fontes citadas na rodada 3 | Tempo rodada 3 |
|---|---|---|---|---:|---:|---:|
| P01 | Tradicional | Rejeitado / inglês | Válido / português | 8 | 6 | 5.25 s |
| P01 | Temático | Rejeitado / inglês | Válido / português | 8 | 6 | 5.47 s |
| P02 | Tradicional | Rejeitado / português | Válido / português | 8 | 6 | 7.10 s |
| P02 | Temático | Rejeitado / português | Válido / português | 8 | 6 | 6.79 s |

As quatro respostas novas têm seis achados e citam seis avaliações únicas cada; oito avaliações foram fornecidas por consulta. O teto de seis achados com uma fonte por achado limita a seis avaliações citáveis. Isso não é uma redução de disponibilidade de evidência nem uma medida de profundidade. Na primeira rodada, o contrato permitia múltiplas fontes por achado; suas contagens não são diretamente equivalentes.

Na rodada 2, cada resposta foi rejeitada por ao menos um trecho declarado não literal. Na rodada 3, esse campo deixou de ser exigido e a aplicação apresenta o original diretamente. A maior aceitação de formato é parcialmente consequência da mudança de contrato; não demonstra aumento de fidelidade semântica. O idioma foi conferido qualitativamente pelo assistente nos campos gerados, sem avaliador independente ou escore linguístico. A primeira resposta tradicional contém marcadores “N/A”, que passaram no formato mas não oferecem informação útil sobre limites/validação.

Os tempos são de uma chamada por combinação, em ordem fixa e sem controle da carga compartilhada. Não permitem estabelecer vantagem estável de latência. Tokens de entrada e saída estão no JSON agregado; não equivalem a custo monetário, memória, energia ou uso de CPU.

## Conferência de significado e apoio

### Primeira pergunta: problemas, condições e divergências

As respostas ficaram mais legíveis e em português, com fonte individual disponível para cada achado. O tradicional ainda transferiu detalhes entre avaliações: a necessidade de remodelagem constante veio de uma fonte diferente da citada, e a condição de pressionar contra o couro cabeludo foi atribuída a um relato que falava de uso em viagem. Uma ressalva de que algo poderia incomodar no uso diário foi resumida com força maior do que a fonte permite.

O temático usou fontes com encaixe, superfície do difusor, colapso e portabilidade, preservando algumas diferenças de uso. Ainda há interpretação ambígua entre não manter a forma e o fato de a superfície plana deixar o cabelo cair para os lados. A explicação sobre silicone e colapso aparece sem deixar claro que é atribuição do consumidor, não diagnóstico técnico. Não se atribui uma nota geral ou vitória ao método a partir dessa leitura.

### Segunda pergunta: melhorias, qualidades e validação

Ambos passaram a apresentar propostas e verificações, mas nem todas respondem bem à tarefa. O tradicional confundiu duas interfaces mecânicas: a fonte relatava separação entre cabeça e corpo do difusor, enquanto a proposta falou da conexão com o secador. O temático preservou melhor a referência a partes e prazos nesse caso, mas manteve outras limitações.

Há propostas associadas a elogios, algumas sendo apenas sugestões de validação apresentadas no campo de melhoria e outras propondo otimizar uma característica sem problema documentado. Em ambos, uma hipótese do consumidor sobre partes coladas ou qualidade do material foi expressa como causa mais estabelecida do que a fonte sustenta. As qualidades valorizadas precisam ser distinguidas de problemas a corrigir. O formato menor não garante essa distinção automaticamente.

As reclamações de colapso em outras fontes disponíveis também não foram plenamente aproveitadas, porque ambos preencheram os seis espaços sobretudo com as primeiras fontes. Essa observação é descritiva desta execução, não uma regra geral de comportamento do modelo.

## Resultado do desenvolvimento

O ajuste resolveu os problemas mecânicos que motivaram esta rodada: não há exigência de copiar trechos, a apresentação da fonte usa texto original do sistema e as quatro respostas estão em português. A checagem confirmou identidade dos textos exibidos e igualdade da recuperação com a rodada 2.

O problema de fidelidade não está resolvido: uma fonte correta no painel pode acompanhar uma afirmação que o modelo atribuiu incorretamente. Não houve revisão humana independente, referência exaustiva ou cálculo de cobertura/fidelidade/profundidade. Este relatório não promove o piloto à avaliação final nem altera conclusões dos experimentos congelados.

O próximo ponto a investigar é o vínculo semântico entre cada achado e a fonte, sobretudo condições de uso, peças/partes e suspeitas de causa, além de distinguir preservação de qualidades de correção de problemas. Uma próxima mudança deve ser documentada e testada em destino novo, sem apagar estas respostas. Não há nova rodada automática nesta entrega.

## Preservação, testes e reprodução

Os arquivos das rodadas anteriores e os artefatos experimentais registrados antes da rodada 3 foram comparados por hash após a execução. O relatório completo com textos originais e a revisão de cada resposta ficam em arquivos locais privados, fora do Git. A interface não foi alterada automaticamente para usar um piloto ainda em desenvolvimento.

A suíte passou com 77 testes antes da geração e 78 na conferência final, incluindo validação de IDs, rejeição de campo de citação inventado, apresentação do texto original e preservação de resultados. Esses testes não validam significado ou qualidade. A exportação dos agregados foi reproduzida sem novas chamadas ao modelo.

Configuração: configs/curly-product-pilot.v3-simple.json. Executor: scripts/run_product_simple_pilot.py. Resultados privados: results/product-pilot/curly-v3-simple/.

```sh
.venv/bin/python scripts/report_product_simple_pilot.py --output results/product-pilot/curly-v3-simple/novos-agregados.json
```

O exportador e o executor recusam destinos existentes. Para novas gerações, usar outra configuração/destino; a semente fixa não garante igualdade textual. Os agregados públicos não contêm comentários ou respostas individuais.
