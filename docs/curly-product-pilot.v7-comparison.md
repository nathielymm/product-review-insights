# Curly Co.: revisão de vínculos e decisão de configuração

## Resultado

A revisão do assistente cobriu as 53 unidades de frase das quatro respostas, incluindo observações, propostas, incertezas e limites. Não é avaliação independente, revisão humana integral nem métrica final de fidelidade. Os dados individuais e trechos permanecem locais, fora do Git.

As quatro gerações originais em inglês são idênticas às da rodada 6. Os candidatos e contextos também coincidem. As quatro gerações e quatro traduções passaram no formato e não tiveram corte, mas isso não demonstra correção semântica. Tradução é somente apresentação: estrutura e citações foram preservadas, sem realimentar a geração.

## O que a conferência encontrou

| Dimensão | Conclusão qualitativa |
|---|---|
| Achados úteis | Existem relatos sustentados sobre encaixe, secagem, definição dos cachos, armazenamento e colapso sob condições específicas. |
| Atribuição | Persistem combinação de condições de pessoas diferentes e transferência de mecanismo de quebra entre relatos. |
| Certeza | Uma suspeita da pessoa sobre peças coladas aparece como constatação no inglês dos dois métodos. |
| Referente | Uma proposta confunde corpo do difusor com corpo do secador; pertencer ao mesmo produto não resolve identidade da peça. |
| Citação | Há proposta apoiada por evidência presente no contexto, porém ausente das citações do achado. Trocar uma referência não corrige todas as falhas de sentido. |
| Limites | A resposta temática nega comparações com produtos anteriores apesar de existirem no contexto; um código de produto não comprova uma única versão. |
| Tradução | Erros lexicais de apresentação permanecem distintos dos erros já presentes no inglês. Tradução fiel não pode corrigir os fatos silenciosamente. |

Não foram computadas taxas de fidelidade: as unidades são frases de papéis diferentes, algumas com várias proposições, e a rubrica/denominadores finais ainda não estão congelados. Esta revisão não estabelece vencedor entre métodos.

## Checagem automática e alinhamento auxiliar

O mesmo Gemma realizou 14 chamadas de auditoria em blocos. Todas foram rejeitadas pelo contrato de validação: combinaram aceitação com motivos de erro incompatíveis. Não houve corte ou falha de transporte nessas chamadas. Nenhum rótulo ou vínculo proposto foi aceito como validação, e nenhuma fonte foi substituída. Zero vínculos alterados não significa ausência de erros.

Foi executado, sem nova geração, um alinhamento auxiliar por embeddings entre cada frase e as frases das fontes originais. Ele mantém até três candidatos de avaliações distintas e um alerta lexical de possível perda de incerteza. Similaridade não comprova suporte: pode aproximar condições opostas, pessoas ou peças diferentes. O alerta também pode falhar. Esses candidatos servem apenas à inspeção e não corrigem a resposta nem entram em métricas finais.

Geração e tradução consumiram juntas 37.86 segundos de tempo registrado para as quatro respostas. A auditoria adicionou 115.49 segundos, 73062 tokens de entrada processados e 5730 tokens de saída, sem produzir vínculos aceitos. São medições desta execução local, sem inferência de desempenho geral. O alinhamento auxiliar não teve tempo próprio instrumentado; portanto estes números não representam o custo completo dessa etapa. Não houve monitoramento de processos/memória.

## Decisão para fechar a configuração

Não promover a auditoria automática à configuração final e não declarar que os vínculos foram corrigidos. Preservar o gerador inglês original, a tradução separada e os agrupamentos internos ao produto como base candidata; não modificar o modelo para esconder os erros encontrados.

É possível encerrar esta etapa de diagnóstico sem exigir um gerador perfeito nem repetir pilotos até obter uma resposta favorável. O congelamento experimental depende de registrar previamente a rubrica e o tratamento dos erros conhecidos, além de fechar produtos, perguntas e repetições. Se o objetivo de entrega exigir correção automática desses erros, esta implementação ainda não atende esse requisito e exigirá outro desenvolvimento separado.

Critérios propostos antes do congelamento:

1. Mesma busca por aspectos, orçamento, gerador inglês e regra de tradução nos dois métodos; variar somente a seleção temática das evidências.
2. Fonte recuperada deve permanecer literalmente rastreável, por resposta e avaliação, sem substituição automática. Distinguir validade mecânica da citação e suporte semântico da afirmação.
3. A rubrica deve registrar troca de pessoa/produto/peça, inversão de condição, certeza aumentada, generalização, omissão e proposta sem problema sustentado. Julgar hipóteses como hipóteses; informações de vendas não são exigidas para sugerir investigação.
4. A avaliação principal deve usar o inglês original; a tradução terá checagem separada de apresentação e não poderá reparar resultados.
5. Saídas com erro, falha ou corte permanecem no denominador definido antes da execução. Não há exigência de zero erro semântico para realizar uma comparação científica.
6. Curly Co. permanece desenvolvimento. Não tratar este caso ajustado como teste independente nem chamar os outros dados já explorados de completamente intocados.

O congelamento completo ainda não foi realizado. Não houve mudança da interface ou dos experimentos congelados anteriores. Os 74 arquivos registrados antes desta rodada passaram na conferência de hashes.

## Reprodução e arquivos

- Configuração: `configs/curly-product-pilot.v7-reference-audit.json`.
- Execução local: `.venv/bin/python scripts/run_product_reference_pilot.py --help` (o runner recusa sobrescrever destinos existentes; não regenerar para selecionar a melhor saída).
- Agregados: `.venv/bin/python scripts/report_product_reference_pilot.py --output /tmp/curly-v7-aggregates.json`.
- Candidatos auxiliares: `scripts/rank_product_reference_spans.py --output <novo-destino-local>`.
- Resultados e revisão individual: `results/product-pilot/curly-v7-reference-audit/`, ignorados pelo Git.
- Conferência para leitura: `outputs/piloto-curly-co-rodada7-vinculos.md` na pasta de trabalho superior, também fora do repositório.

As gerações desta rodada já estavam concluídas antes da revisão; não houve novas chamadas ao LLM nesta conclusão.

Verificação: 97 testes passaram. O teste novo revelou conflito ao importar bibliotecas de modelo junto ao FAISS; a importação do encoder foi movida para a execução que realmente o utiliza. O alinhamento já salvo preserva o hash e uma cópia local do script executado antes dessa mudança de carregamento. Os agregados foram exportados novamente e coincidiram byte a byte.
