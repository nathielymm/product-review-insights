# Configuração final candidata v2 — para revisão

Estado: configuração preparada para revisão, sem congelamento e sem autorização/execução de gerações finais. A rubrica, as unidades e os denominadores foram aprovados; essa aprovação foi registrada em uma versão nova, preservando a proposta anterior. Nenhuma pergunta, referência ou saída experimental anterior foi reescrita.

## Produtos e base

| Produto | Avaliações | Trechos indexados | Agrupamentos locais (tamanhos) |
|---|---:|---:|---|
| Escova GranNaturals | 613 | 613 | 28, 264, 97, 224 |
| Shampoo Pure Body Naturals Argan | 473 | 474 | 92, 175, 132, 75 |
| Máscara de cílios Bold Lash | 123 | 123 | 17, 43, 37, 26 |

Cada consulta usa apenas um produto. Todas as 1.209 avaliações elegíveis permanecem disponíveis, sem quotas por nota e sem exclusão por mudança de fórmula. Versão, compra anterior e pessoa devem continuar atribuídas conforme o relato. O Curly Co. permanece somente desenvolvimento.

Os agrupamentos são exploratórios: MiniBatchKMeans, quatro por produto, semente 42, dez inicializações e batch de 1.024. Foram herdados do desenho do piloto, sem busca de melhor configuração nos resultados finais. A inspeção lexical não os certifica como quatro temas distintos. Os tamanhos não precisam ser iguais. Vocabulário e temas podem se sobrepor; IDs de agrupamento não são alvos da rubrica.

## Comparação compartilhada

| Etapa | Configuração candidata |
|---|---|
| Embeddings | Snapshot local MiniLM de 384 dimensões; pesos registrados por hash |
| Índice | FAISS IndexFlatIP, vetores normalizados, busca equivalente a cosseno |
| Segmentação | Regra original limitada pelo tokenizer do encoder, sem sobreposição e mantendo identidade da avaliação |
| Busca | Cinco consultas em inglês por pergunta, 16 candidatos por consulta, fusão RRF com constante 60 |
| Candidatos | Mesma lista para os dois métodos, até 80 avaliações únicas |
| Tradicional | Primeiras oito avaliações do ranking comum |
| Temático | Uma representante por agrupamento disponível nos candidatos; completar por ranking até oito |
| Contexto | Até oito avaliações e 12.000 caracteres de evidências serializadas; registrar o que entrou efetivamente |
| Geração | Gemma 3 4B local, gerador/prompt/esquema inglês originais, temperatura 0 e semente 42 |
| Limites | 8.192 tokens de janela; até 1.536 de saída |
| Apresentação | Tradução separada para português, no mesmo Gemma, até 1.536 tokens próprios |
| Correções automáticas | Sem reescrita factual, seleção da melhor tentativa ou auditoria do mesmo modelo como certificação |

A diversidade temática ocorre somente dentro da lista comum; não há obrigação de preencher grupos ausentes. Os candidatos não são automaticamente todos relevantes. Oito avaliações é o orçamento do piloto preservado como candidato, não uma quantidade comprovadamente ótima ou suficiente para cobertura completa.

A regra original de contexto inclui trechos inteiros em ordem, pulando os que não couberem no orçamento de caracteres. Não altera o texto dentro de um trecho. A janela total do modelo inclui mais do que essas evidências; 12.000 caracteres não equivalem a uma garantia de caber em 8.192 tokens. A verificação real de tokens ainda está pendente.

## Perguntas e idioma

As seis perguntas específicas por produto e as referências revisadas permanecem. Foram preparados os 18 equivalentes ingleses e as 90 consultas de busca para revisão. As consultas derivam das perguntas, sem IDs, trechos ou respostas das referências. São iguais para os dois RAGs.

Q5 e Q6 usam as mesmas cinco buscas amplas pelos aspectos do produto, mas cada uma é uma consulta independente: Q6 não recebe a resposta de Q5, e Q5 não recebe respostas de Q1–Q4. Isso permite ao controle sobre vendas avaliar os limites de relatos de produto sem fabricar dados comerciais.

A avaliação semântica usa o inglês original. A tradução muda apenas textos de apresentação; fontes, citações e inglês ficam preservados. Fontes continuam no idioma original. Falha da tradução não apaga o resultado inglês. Não traduzir as repetições diagnósticas.

## Grade e ordem propostas

| Fase | Gerações inglesas | Traduções máximas |
|---|---:|---:|
| Principal: 3 produtos × 6 perguntas × 2 métodos × 1 execução | 36 | 36 |
| Estabilidade: duas execuções extras de Q1/Q5 nos 3 produtos e 2 métodos | 24 | 0 |
| Total | 60 | 36 |

Máximo previsto: 96 chamadas ao LLM. Traduções podem ser puladas quando não houver estrutura inglesa válida; o motivo ficará registrado. Não são 96 respostas principais nem réplicas estatisticamente independentes.

A ordem usa semente 20261119, com métodos adjacentes dentro do mesmo caso e alternância de quem vai primeiro (nove pares principais começam com cada método). Todas as gerações inglesas antecedem as traduções para separar idioma e recursos. Sem aquecimento adicional, tentativas de reparo ou repetição para escolher a melhor resposta; registrar efeitos da primeira chamada/carga do modelo. Estabilidade fora dos denominadores principais, com mudanças preservadas para inspeção.

## Avaliação aprovada

Por método: 55 alvos de conteúdo, 38 de condições/qualificações e 16 de contrastes em Q1–Q4; 15 casos de propostas Q1–Q5 e três controles Q6. A fidelidade e o suporte de citação seguem afirmações factuais únicas. Não há nota geral. As referências são parciais e os 78 itens administrativos não são unidades intercambiáveis.

A revisão humana proposta mantém seis pares principais, totalizando 12 respostas, com um par por pergunta e dois por produto, sorteados antes dos resultados. Métodos ficam ocultos na apresentação; isso não constitui avaliação independente ou validação integral do corpus. Não ampliar automaticamente a carga humana.

## O que a preparação já verificou

Foram construídos três índices separados, sem consultas a modelos de geração. Identidade, contagens, hashes, pesos do encoder e presença das avaliações de referência nos índices foram conferidos. Nenhuma das 60 avaliações revisadas foi dividida entre mais de um trecho; uma outra avaliação do shampoo precisou ser dividida, preservando a origem.

O ensaio offline montou os 36 contextos e os pedidos no contrato do gerador original, interceptando o transporte antes de qualquer chamada ao LLM. Todos tinham oito avaliações únicas, sem produto estrangeiro ou descarte pelo limite de caracteres. Os candidatos por pergunta variaram de 23 a 54; o contexto de evidências mais longo teve 5.262 caracteres. Esses números são verificações de preparação, não latências ou resultados de qualidade.

Em sete dos 18 pares, os conjuntos de avaliações selecionadas foram iguais; em cinco, também tiveram a mesma ordem. Nos demais, houve seis ou sete avaliações comuns. A seleção temática pode mudar a ordem além de mudar fontes. Isso será relatado, sem escolher parâmetros para forçar diferença ou favorecer um método.

## Pendências antes do congelamento

1. Revisar os equivalentes ingleses, as consultas de busca, parâmetros, grade e ordem desta candidata.
2. Conferir a correspondência semântica das unidades aos trechos finais e revisar os agrupamentos como estruturas exploratórias, sem chamar a inspeção de validação independente.
3. Verificar a versão/digest do modelo no runtime ativo e o orçamento completo de tokens, incluindo entrada, contrato e reserva de saída, sem truncamento silencioso. Versão esperada 0.40.11 e digest esperado são os do piloto, ainda não confirmados no runtime por esta etapa offline.
4. Calibrar aplicação da rubrica no caso Curly Co. e implementar/verificar o runner v2, a anotação e a exportação das métricas conforme o protocolo aprovado. Os runners antigos de piloto não são a execução v2 pronta.
5. Após as verificações, registrar hashes e autorização explícita para congelar e executar. A configuração candidata não libera execução por si só.

## Arquivos e preservação

- Configuração: `configs/product-evaluation.v2.review-candidate.json`.
- Perguntas e buscas: `configs/product-questions.v2.execution-candidate.json`.
- Ordem de execução: `configs/product-run-schedule.v2.review-candidate.json`.
- Rubrica aprovada: `configs/scoring-rubric.v2.approved.json`; recibo agregado em `docs/scoring-approval.v2.json`.
- Verificações offline: `docs/product-evaluation.v2-preflight-summary.json`.
- Evidências, unidades individuais aprovadas, índices e ensaio de contextos permanecem em caminhos locais ignorados pelo Git.

Preparação não altera o estudo congelado anterior, a interface ou as rodadas do piloto. Nenhum resultado final foi gerado. Não houve criação ou envio ao GitHub.
