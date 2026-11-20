# Rubrica e preparação da pontuação

As interpretações dos três pacotes foram aprovadas. Esta etapa decompõe os pontos em unidades comparáveis e define uma rubrica operacional; não registra respostas de modelos, resultados de qualidade ou congelamento final do experimento. A referência continua auditada, não exaustiva e sem anotação independente.

## O que foi preparado

- 179 unidades factuais a partir das 120 células E: 64 no conjunto compacto, 52 no capilar e 63 no variado.
- Cada unidade identifica pergunta, família, aspecto, expectativa e grupos de comentários de apoio. Aspectos distintos foram separados explicitamente, sem divisão automática por pontuação ou LLM avaliador.
- As três células P e 16 N não criam pontos factuais obrigatórios: evidência positiva não vira reclamação e lacuna na inspeção não vira ausência comprovada no corpus.
- As 41 células H orientam critérios de propostas; as 30 células C são critérios de limite repetidos nas famílias, avaliados em seis respostas de controle (duas perguntas × três conjuntos), não como 30 observações independentes.
- Foram preparados 42 formulários de caso sem anotações ou respostas. As repetições de geração futuramente terão identificadores próprios.

A decomposição nova e os critérios estão preparados para revisão metodológica antes do congelamento final. A aprovação das interpretações anteriores não é apresentada como aprovação automática de cada denominador novo.

## Cobertura: o que entra na conta

Nas nove perguntas factuais (Q01–Q08 e Q11), uma unidade é coberta quando a resposta preserva o ponto material, a família correta e as qualificações essenciais, com suporte. A redação pode variar. Não basta usar uma palavra-chave ou um ID de citação válido.

Exemplo de decomposição: o mesmo comentário pode sustentar pouco volume e pouco alongamento; esses aspectos ficam separados. Repetir pouco volume em três frases não cria três acertos. Dentro da mesma pergunta, a identidade é família + aspecto, sem duplicação. Um mesmo aspecto pode aparecer legitimamente em perguntas diferentes, mas essas observações não são tratadas como independentes.

Para relatos contrastantes, os dois lados precisam ter evidência disponível. Alternativas de apoio dentro de um grupo usam regra OU; grupos distintos usam regra E. Uma avaliação pode, por si só, descrever as duas experiências, como no relato da autora e da namorada do filho.

Reportar por conjunto/pergunta:

1. Cobertura por unidade = unidades cobertas / unidades elegíveis da referência auditada.
2. Média entre famílias = média das coberturas das famílias com unidades elegíveis. Essa é a apresentação principal para não dar mais peso a uma família apenas por ter mais aspectos anotados.
3. Cobertura dos aspectos da referência = aspectos com ao menos uma unidade coberta / aspectos elegíveis. Mostrar junto com a cobertura por família, pois mencionar um aspecto em uma família não cobre automaticamente as demais.

Os aspectos são chaves descritivas da referência, sem usar os clusters do recuperador temático como verdade de avaliação. Essa cobertura não representa todos os temas possíveis do corpus.

Denominador vazio resulta em não aplicável, nunca zero ou acerto automático. Sem anotação, a métrica permanece ausente. Uma lista explicitamente revisada sem acertos resulta em zero somente se houver unidades elegíveis. Mostrar os números de famílias e unidades efetivamente avaliados.

## Recuperação e resposta são etapas distintas

A anotação registra separadamente quais unidades estão sustentadas nos trechos recuperados e quais aparecem corretamente na resposta. Isso permite identificar omissão na busca ou na geração. O ID de uma avaliação presente no índice não garante que o trecho contendo a evidência foi entregue ao modelo; a leitura do trecho é necessária.

## Fidelidade e citações

Separar afirmações factuais em sustentadas, contraditas ou sem suporte, considerando negação, família, versão e experiência direta/indireta. Fidelidade = afirmações sustentadas / afirmações factuais. A taxa de contradição é reportada à parte; ausência de suporte não é automaticamente contradição.

Sem afirmações factuais, a fidelidade fica não aplicável, não perfeita. Com julgamentos pendentes, o resultado fica ausente. A cobertura e a adequação à tarefa impedem tratar uma resposta vazia como boa análise.

Verificar também se cada passagem citada sustenta a afirmação associada: uma resposta pode ser sustentada pelo contexto, mas citar o trecho errado. A existência do ID é apenas uma verificação de formato, não de suporte semântico. As propostas devem ser explicitamente inferidas; benefícios esperados não podem ser apresentados como resultados comprovados.

## Propostas e controles

Q09, Q10 e Q12 recebem quatro julgamentos separados (sim, não ou pendente/não aplicável com motivo):

- vínculo com problema ou tensão documentada e família correta;
- distinção entre relato e proposta/hipótese;
- pertinência à tarefa (produto, possíveis perdas ou informação, conforme a pergunta);
- incertezas e necessidade de validação explícitas.

Aceitar alternativas fundamentadas, sem exigir a solução exemplificada na referência. Não criar média ponderada única para misturar esses critérios com cobertura factual.

Q13 e Q14 recebem dois julgamentos separados: reconhece o limite e evita garantia/previsão injustificada. Avaliar por resposta, sem multiplicar o mesmo controle pelas cinco famílias. É permitido aproveitar informações úteis dos relatos; o acerto não exige rejeitar tudo.

## Verificação das amostras menores

Foram conferidos hashes e pertencimento dos 27 corpora de sensibilidade, nos três tamanhos e três sementes. A disponibilidade usa os comentários de apoio conhecidos da referência. São 243 combinações de pergunta factual/subconjunto; 58 não retêm apoio conhecido para nenhuma unidade daquela pergunta.

Isso não significa que esses subconjuntos não contenham o tema nem que o RAG falhará. Significa que não se pode transportar cegamente o denominador do corpus completo. Antes da pontuação final de cada caso, verificar evidências alternativas. Sem referência elegível, registrar cobertura não aplicável e divulgar a lacuna. Não alterar amostras ou escolher sementes em função de respostas mais favoráveis.

| Conjunto | 20 por família | 40 por família | 60 por família |
|---|---:|---:|---:|
| Máscaras | 12.5%–25.0% | 34.4%–56.2% | 65.6%–71.9% |
| Rotina capilar | 7.7%–11.5% | 17.3%–19.2% | 25.0%–28.8% |
| Variado | 3.2%–14.3% | 11.1%–27.0% | 22.2%–39.7% |

A tabela mostra somente a fração de unidades cujos comentários-âncora conhecidos permanecem no subconjunto, com faixa entre sementes. Não mede qualidade do RAG, proporção de todos os temas ou proporção de comentários relevantes. Como a referência é parcial, outras avaliações podem sustentar o mesmo aspecto; isso exige adjudicação explícita e rastreável.

## Reprodução e arquivos

```sh
.venv/bin/python scripts/prepare_scoring_reference.py --output results/scoring-reference/novo-snapshot
.venv/bin/python -m pytest -q
```

O destino deve ser novo. O script verifica aprovações contra os hashes dos pacotes, os corpora, as identidades das famílias, os índices de evidências e o pertencimento dos subconjuntos. Os arquivos privados incluem unidades, disponibilidade e formulários vazios. Nenhuma nota humana é preenchida pelo script.

Configuração: configs/scoring-facets.v1.draft.json e configs/scoring-rubric.v1.draft.json. Implementação: src/product_review_insights/scoring.py. Estado atual: configs/scoring-current.draft.json. Resumo público: docs/scoring-preparation-summary.json.

A suíte teve 39 testes aprovados, incluindo denominador vazio, anotação ausente, suporte conjunto de contrastes, evidência alternativa, deduplicação, família incorreta e preservação de critérios sem nota inventada. O comando legado evaluate continua sendo o avaliador por contagens do piloto; não o apresentar como aplicação automática desta rubrica por unidades. A anotação de respostas reais e sua vinculação ao runner final ainda precisam ocorrer.

## Próximo marco

Revisar os critérios/decomposição e selecionar parâmetros apenas no desenvolvimento. Depois congelar rubrica, referências elegíveis por corpus, perguntas e configurações antes de executar os métodos. A referência pode aceitar evidência adicional válida, mas correções devem ser registradas antes da revelação do método; não ajustar silenciosamente denominadores para beneficiar um resultado.
