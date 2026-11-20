# Revisão final de coerência do projeto — v2

Atualização posterior: a integração da interface e os guias foram atualizados conforme [registro de implementação](demo-v2-alignment.md). Os achados abaixo preservam o estado observado na revisão anterior; as pendências acadêmicas e os limites de reprodução continuam identificados.

## Resultado da revisão

O texto acadêmico corrente, a configuração efetivamente congelada e os agregados da v2 estão coerentes quanto aos três produtos, às 36 respostas principais, aos denominadores e às limitações. A interface e as instruções gerais de reprodução ainda correspondem ao fluxo anterior. A entrega técnica precisa desses ajustes antes de representar a v2 em uma demonstração.

Esta etapa foi de revisão. Não foram alterados o servidor da interface, o HTML, os prompts, os índices ou o código congelado. Nenhuma pergunta foi enviada ao Gemma. Foram produzidos apenas este relatório e o registro de progresso.

## Verificações realizadas

- 119 testes automatizados passaram no ambiente local existente. Os testes atuais da interface exercitam seu fluxo anterior; sua aprovação não comprova integração com a v2.
- O comando de conferência da configuração verificou 73 arquivos, três produtos, 18 perguntas e 60 tentativas em inglês programadas, sem gerar respostas. Esse comando valida entradas; a autoridade de congelamento continua sendo o manifesto externo v2, apesar dos nomes/status históricos preservados nos arquivos candidatos.
- As métricas foram exportadas novamente para um destino local novo e coincidiram exatamente com o JSON publicado, preservando as anotações finais.
- Foram conferidos os hashes dos 73 arquivos congelados e dos 77 arquivos anteriores registrados.
- Foram verificados 22 links locais nos documentos principais selecionados, sem destinos ausentes.
- A página foi aberta no navegador com servidor temporário em loopback. O formulário mostrou os conjuntos antigos e a opção de consultar todos os produtos de um conjunto. O servidor foi encerrado após a inspeção.
- Não há dados brutos, corpora, modelos, índices ou arquivos individuais de resultados rastreados nos caminhos/extensões conferidos. Nenhum remoto Git está configurado. Isso não substitui a revisão final de conteúdo antes de publicação.

Não foi feita instalação em ambiente limpo, reprodução da preparação desde o Parquet, geração ao vivo pela interface ou validação em outra arquitetura. A inspeção do navegador abrangeu o formulário e o catálogo inicial; comportamento de respostas/fontes foi examinado pelo código e pelos testes existentes, sem alegar uma consulta real completa.

## Ajustes necessários

### 1. Alinhar o catálogo, os índices e a busca da interface — prioridade alta

Evidência: `scripts/serve_demo.py:21` define os três conjuntos antigos; `scripts/serve_demo.py:26` carrega `configs/study-scope.json`; `scripts/serve_demo.py:117` lê o congelamento v1. O HTML, em `demo/index.html:11`, permite conjunto e todos os seus produtos. A consulta individual em `scripts/serve_demo.py:93` restringe um índice antigo em memória, reutilizando seus agrupamentos.

Os três produtos finais constam dos 15 rótulos da interface, mas nenhum dos índices usados por esse caminho coincide com o índice v2 correspondente. A presença do nome correto no seletor não significa que a consulta use o corpus e os temas locais avaliados.

Ajuste proposto: selecionar diretamente GranNaturals, Pure Body Naturals ou Bold Lash; carregar o índice individual da v2; usar a seleção tradicional/temática sobre candidatos comuns segundo a configuração por produto. Retirar a consulta conjunta do fluxo principal da apresentação acadêmica.

Critério de aceite: o contexto pertence integralmente ao produto escolhido; o método temático usa seus quatro agrupamentos locais; os índices são somente lidos; perguntas avaliadas reproduzem a seleção do executor v2 sob a mesma entrada; nenhum resultado experimental é escrito ou substituído.

### 2. Alinhar geração, idioma e consultas da demonstração — prioridade alta

Evidência: `scripts/serve_demo.py:31` modifica o prompt para geração direta em português; `scripts/serve_demo.py:144` faz uma busca da pergunta sem as cinco buscas por aspectos/RRF da v2. A configuração avaliada usa geração original em inglês e tradução separada de apresentação. As perguntas e consultas por aspectos foram predefinidas em inglês.

Ajuste proposto: reutilizar a geração original em inglês e traduzir somente os campos de apresentação, mantendo citações e inglês intactos. Oferecer as perguntas avaliadas como exemplos com suas entradas e buscas congeladas. Para perguntas livres, definir e documentar o tratamento do idioma e dos aspectos como consulta demonstrativa, sem afirmar que toda pergunta nova reproduz uma pergunta experimental.

Critério de aceite: a interface não modifica o prompt inglês congelado; tradução não muda evidências/citações nem corrige fatos; comparação das perguntas avaliadas usa o caminho de recuperação da v2; perguntas livres têm política explícita na documentação. Resultados ao vivo continuam separados das métricas.

### 3. Atualizar o guia de execução e reprodução — prioridade alta para a entrega

Evidência: `docs/local-demo.md:27` exige índices v1, e `docs/local-demo.md:31` descreve geração direta em português. `docs/reproduction.md:23` encaminha ao piloto global; `docs/reproduction.md:57` ainda pede congelar um rascunho anterior. O comando atual de recálculo da v2 existe em `docs/product-evaluation.v2-results.md`, mas o guia geral não apresenta um percurso consolidado até os corpora, índices, referências, execução e métricas da v2.

Ajuste proposto: criar uma entrada de reprodução da v2 que distinga ambiente, acesso aos arquivos locais, preparação, índices por produto, congelamento, geração, anotação e recálculo. Manter instruções históricas identificadas como tal. Comandos que reconstruam artefatos precisam de destinos novos e não devem ser apresentados como capazes de recriar anotações semânticas humanas/assistidas automaticamente.

Critério de aceite: uma pessoa encontra os comandos da versão entregue, sabe quais artefatos não estão no ZIP/Git e quais dependem de acesso local, e consegue recalcular os agregados quando recebe os registros/anotações necessários. A reprodução desde a fonte em ambiente novo precisa ser verificada ou ter seu alcance explicitamente delimitado. Não se exige repetir as gerações congeladas para corrigir este guia.

### 4. Atualizar a cobertura de testes da interface — junto dos ajustes 1 e 2

Evidência: `tests/test_demo.py:14` valida conjuntos antigos, e `tests/test_demo.py:49` exige o prompt direto em português. A suíte funciona como proteção desse comportamento, não como teste de aderência à metodologia atual.

Ajuste proposto: manter os testes úteis de validação, isolamento, fontes e liberação do bloqueio; acrescentar verificações do catálogo v2, índice por produto, seleção por aspectos, geração inglesa e tradução de apresentação. A verificação do caminho das perguntas avaliadas pode comparar contextos existentes, sem chamar o modelo nem alterar os runs.

Critério de aceite: testes falham se a interface carregar índices antigos, misturar produtos, mudar silenciosamente o contrato de geração ou alterar citações durante tradução. Após implementação, conferir formulário, respostas, fontes e erros no navegador, delimitando se a consulta foi real ou simulada.

### 5. Fechar referências bibliográficas e identificação acadêmica — pendência editorial

Evidência: o README contém fontes internas de resultados e o link do curso, mas não uma bibliografia consolidada dos fundamentos usados: RAG, dataset, embeddings, FAISS, agrupamento, fusão de rankings e modelo. O texto não deve confundir referências bibliográficas com comentários usados como evidência.

Ajuste proposto: organizar fontes bibliográficas verificadas e citá-las nas seções correspondentes, respeitando o modelo de entrega. Confirmar o formato de submissão exigido e preencher aluna, orientação e matrícula quando os dados forem fornecidos. Os campos em branco são intencionais e não foram tratados como erro.

Critério de aceite: escolhas metodológicas têm referências verificáveis, sem atribuir resultados próprios a fontes externas ou inventar títulos/dados acadêmicos. O formato exigido pela instituição é confirmado antes de produzir um documento adicional.

## Limitações mantidas, sem exigir nova grade experimental

Continuam explícitas a referência parcial, a anotação do assistente, a revisão humana das interpretações de 12 respostas, os três produtos escolhidos intencionalmente, as diferenças de apresentação/fórmula, a ambiguidade de marca em algumas fontes e a execução local. A procedência exata do Parquet ainda não foi comprovada e permanece uma pendência de verificação ou uma limitação declarada. O lock e os testes locais não certificam instalação em outra arquitetura.

A inspeção das seis saídas diagnósticas diferentes já está concluída e documentada. O relatório numérico original menciona a pendência no estado em que foi publicado; o complemento diagnóstico e o texto acadêmico corrente registram sua conclusão. Isso não é uma nova pendência ou mudança de denominadores.

Não foram identificadas divergências numéricas entre o texto atual e os agregados auditados. Avaliação independente, novos modelos e novas grades de sensibilidade permanecem continuidade científica; não são condições impostas por esta revisão para fechar a versão estudada.

## Ordem sugerida

Primeiro, alinhar a interface à v2 em um módulo de demonstração separado dos arquivos congelados. Em seguida, testar essa integração e atualizar os guias atuais de execução/reprodução. Por último, fechar bibliografia, dados acadêmicos e pacote de entrega. A criação/envio do repositório privado continua dependente da revisão e autorização da usuária.
