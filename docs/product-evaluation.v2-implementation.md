# Execução e métricas da avaliação por produto v2

Estado: configuração aprovada, verificações técnicas concluídas e implementação disponível, sem congelamento ou respostas finais. A grade, as perguntas, os parâmetros científicos, as referências e os denominadores aprovados permanecem. A configuração atual é `configs/product-evaluation.v2.approved-not-frozen.json`; a candidata anterior foi preservada.

## O que foi implementado

- `src/product_review_insights/evaluation_v2.py`: verificação dos arquivos e versões, isolamento por produto, grade de 60 tentativas inglesas, transporte com guarda de tokens e execução sequencial.
- `scripts/run_product_evaluation_v2.py`: modo de checagem e entrada de execução que exige um manifesto de congelamento autorizado separado. A aprovação da configuração sozinha não libera as gerações finais.
- `src/product_review_insights/scoring_v2.py`: conferência das anotações e cálculo de cobertura, condições, contrastes, fidelidade, suporte das citações, propostas, controles, estabilidade e recursos.
- `scripts/score_product_evaluation_v2.py`: criação de fichas de anotação com métodos ocultos e chave separada; exportação de métricas somente após completar todos os casos principais.

O gerador inglês original e o tradutor de apresentação anteriores não foram alterados. Não há nova auditoria automática de verdade por LLM. A semântica das afirmações, dos aspectos e das propostas exige anotação do assistente/revisão humana; o código valida a rastreabilidade e calcula os resultados a partir desses julgamentos.

## Verificações realizadas

| Verificação | Resultado |
|---|---|
| Runtime local | Ollama 0.40.11, mesmo digest Gemma 3 4B do piloto |
| Contextos ingleses | 36 verificados pelo runtime; entradas entre 1.215 e 1.791 tokens |
| Maior entrada + reserva de saída | 1.791 + 1.536 = 3.327, abaixo da janela de 8.192 |
| Checagem na janela final | Maior contexto conferido novamente em 8.192, com a mesma contagem |
| Referências | 60 comentários revisados preservados integralmente nos trechos pelo roundtrip do tokenizer; vínculos dos 109 alvos conferidos |
| Agrupamentos | Vocabulário e três representantes de cada um dos 12 grupos inspecionados |
| Calibração | Cinco exemplos factuais e uma proposta do desenvolvimento Curly Co. documentados |
| Testes | 119 passaram, incluindo 22 testes novos da v2 |
| Trava real sem congelamento | Recusou execução antes de criar pasta de resultados ou chamar o modelo |

As sondagens usaram um token de saída cada, em registros técnicos separados: 36 para contar os contextos com janela ampliada e uma para conferir o maior caso na janela final. Foram 37 tokens gerados em 37 chamadas técnicas, não respostas de avaliação. Os recursos medidos estão no resumo técnico. Nenhuma pontuação final da v2 foi calculada.

Os grupos são exploratórios e se sobrepõem, especialmente no shampoo. A inspeção de representantes não é validação independente, anotação de todos os membros ou prova de quatro temas exclusivos/ótimos. Não se alterou o agrupamento para favorecer os resultados dos RAGs. A presença de um comentário de referência no índice também não comprova que o método o recuperará ou que a resposta preservará seu significado.

## Travas e preservação

Antes de executar, o manifesto futuro precisa autorizar explicitamente congelamento e geração e corresponder aos hashes da configuração, fontes, índices, código e verificações. As versões das bibliotecas são verificadas. O runtime é conferido antes e depois; alterações durante a execução invalidam sua integridade. Nenhum manifesto de congelamento foi criado nesta entrega.

Destinos existentes não são sobrescritos nem retomados automaticamente. Uma falha ordinária fica registrada na tentativa prevista, e a execução não a substitui por uma nova resposta. Falhas de integridade ou orçamento interrompem a execução sem liberar exportação final. As saídas recebidas permanecem no registro de transporte mesmo quando uma checagem posterior falha. Ao terminar, hashes dos arquivos de respostas, traduções e sondagens são registrados para detectar alterações antes da anotação/exportação.

A fase inglesa tem 36 tentativas principais e 24 diagnósticas. Depois vêm até 36 traduções das respostas principais estruturadas. A tradução não muda inglês, fontes ou citações, e os diagnósticos de estabilidade não recebem traduções.

As entradas futuras das traduções dependem do texto que ainda será produzido. Para evitar truncamento silencioso, a guarda poderá fazer até 36 sondagens técnicas adicionais de um token, uma por novo texto de tradução. Elas são independentes da chamada de tradução original, não alimentam o seu conteúdo, não são tentativas de reparo e não entram nos denominadores de qualidade. Serão contabilizadas em recursos separados. Portanto, permanecem até 96 chamadas de geração/tradução previstas, mais até 36 checagens técnicas durante a execução; as 37 sondagens de preparação já realizadas são outro custo técnico registrado.

## Como a anotação funciona

As fichas de trabalho ocultam método, escores e agrupamentos; a chave de correspondência fica em outro arquivo privado. Isso é cegamento parcial, não independência: a usuária já conhece o material. A amostra humana permanece de seis pares (12 respostas), pré-selecionada sem consultar notas; as anotações completas continuam necessárias para exportar os resultados.

Cada anotação liga-se ao hash do registro inglês e à matriz aprovada. Afirmações factuais e propostas apontam para trechos exatos dos campos originais por caminho e posições de início/fim. O código rejeita uma citação inventada ou uma tentativa de atribuir a afirmação a uma fonte diferente das citadas originalmente. Para saídas sem estrutura válida, âncoras explícitas no texto bruto e sua conferência manual preservam o vínculo; o texto não é reescrito para caber no esquema.

Os inventários de afirmações/propostas e a deduplicação precisam ser confirmados. Nenhum rótulo pendente vira sucesso ou desaparece do denominador. Julgamentos semânticos continuam responsabilidade da anotação: conferir um ID, uma substring ou um hash não certifica suporte factual.

Cobertura usa os alvos fixos completos, não apenas o que foi recuperado. Contexto e resposta são pontuados separadamente. Evidência alternativa para o mesmo alvo precisa de verificação documentada; não aumenta o denominador nem transforma um novo assunto em alvo primário depois dos resultados. Contrastes exigem ambos os lados e a relação, mesmo quando estão no mesmo relato.

A fidelidade ao contexto fica separada do apoio das próprias citações. A ausência de afirmações gera precisão não aplicável, não 100%. Propostas são avaliadas em Q1–Q5, e uma resposta sem proposta recebe zero no cumprimento da tarefa. Todas as oportunidades são consideradas; mais de duas em Q5 não permite selecionar só as melhores. Q6 possui seus quatro critérios próprios e não ganha um denominador de cobertura factual.

Os resultados são agregados primeiro por questão/produto e depois com peso igual entre os três produtos. Denominadores e elegibilidade das médias condicionais são expostos. Falhas, respostas vazias e repetições diagnósticas não são misturadas para melhorar artificialmente uma média. Não existe nota única de qualidade nem inferência populacional a partir desses três casos.

## Recursos e exportação

O exportador registra tempos de preparação dos índices, recuperação, execução inglesa e apresentação; tokens conhecidos, medidas ausentes, cortes, falhas e contagem de chamadas também ficam explícitos. O tempo da apresentação incluindo sua guarda fica distinguível do tempo da chamada efetiva de tradução. Sondagens técnicas têm registros próprios. Não há monitoramento de processos, CPU, memória ou estimativa inventada de energia/custo financeiro.

A exportação privada conserva os resultados por caso. A exportação pública é construída somente com agregados e proveniência: não copia textos, evidências, justificativas, localizadores ou anotações individuais.

## Comandos disponíveis

Checagem local de integridade, sem geração:

```sh
.venv/bin/python scripts/run_product_evaluation_v2.py --config configs/product-evaluation.v2.approved-not-frozen.json --check
```

Conferência adicional do runtime local, também sem gerar resposta:

```sh
.venv/bin/python scripts/run_product_evaluation_v2.py --config configs/product-evaluation.v2.approved-not-frozen.json --check --runtime
```

A opção `--run-frozen` exige um arquivo de congelamento autorizado, destino novo e o ledger de tokens conferido. Não há comando que transforme automaticamente a aprovação atual em congelamento. A ferramenta de métricas oferece `--prepare-annotations` e `--export`; ambas exigem um run completo e arquivos consistentes. Exemplos sintéticos dos testes não são resultados do TCC.

## Próximo marco

Revisar esta entrega técnica e, quando houver autorização explícita, registrar o congelamento separado. Depois executar as gerações principais/diagnósticas, anotar as respostas, revisar a amostra humana e calcular os resultados reais. A interface e os resultados anteriores permanecem preservados. Nada foi enviado ao GitHub.
