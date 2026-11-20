# AI Social Listening Analyst

#### Aluna:
#### Orientador(a):

---

Trabalho em desenvolvimento para a pós-graduação em [Inteligência Artificial Generativa e LLM da PUC-Rio](https://ica.ele.puc-rio.br/cursos/ia-generativa-large-language-models/).

- [Código](src/social_listening)
- [Protocolo experimental](docs/protocol.md)
- [Reprodução local](docs/reproduction.md)
- [Auditoria dos dados](docs/data-audit.json)

### Resumo

Este trabalho investiga a geração de insights sobre consumidores a partir de avaliações de produtos. Compara recuperação aumentada por geração (RAG) tradicional com recuperação enriquecida por agrupamento temático, utilizando o recorte All_Beauty do Amazon Reviews 2023 e o Gemma 3 4B executado localmente via Ollama. O estudo avaliará cobertura temática, fidelidade às evidências, latência e custo computacional. A avaliação de qualidade ainda não foi realizada; não há conclusão sobre superioridade de um método.

### 1. Introdução

Avaliações de consumidores podem apoiar a identificação de elogios, reclamações e oportunidades de melhoria. A recuperação por similaridade pode concentrar o contexto em evidências redundantes. Investiga-se se uma seleção diversificada por temas aumenta a cobertura sem comprometer a fidelidade aos comentários.

O conjunto de dados utilizado é declarado como Amazon Reviews 2023, categoria All_Beauty, do McAuley Lab. O arquivo fornecido contém 701.528 registros e esquema compatível com avaliações. A correspondência exata com o arquivo oficial ainda exige verificação de procedência. A análise de avaliações não representa toda a escuta social nem permite inferir participação de mercado.

### 2. Modelagem

O pipeline realiza leitura local de Parquet, exclusão de texto vazio e notas inválidas, remoção de duplicatas por produto e texto normalizado, redação heurística de emails, URLs e telefones e amostragem determinística por hash. Identificadores de usuários e imagens não são incorporados ao corpus derivado. A redação automática não garante anonimização completa; dados e respostas ficam fora do Git.

Quando duplicatas divergem em título, capitalização ou nota, usam-se representações canônicas determinísticas (mínimo lexicográfico de título/texto e menor nota). A nota não entra no prompt nem na busca; essa regra pode afetar sua distribuição descritiva e deve ser revista antes do congelamento dos dados.

As avaliações são segmentadas no limite do encoder MiniLM, convertidas em embeddings normalizados e indexadas em FAISS com similaridade de cosseno. MiniBatchKMeans agrupa os mesmos vetores; termos TF-IDF e exemplos representativos permitem inspecionar os agrupamentos. Os rótulos automáticos não constituem uma taxonomia validada.

O método tradicional seleciona os primeiros k resultados por similaridade. O temático seleciona primeiro um resultado por grupo dentro do mesmo conjunto de candidatos e completa as vagas por similaridade. Ambos utilizam o mesmo Gemma 3 4B, encoder, corpus, prompt, limite de contexto e parâmetros de geração. O enriquecimento atua na seleção das evidências, sem inserir resumos gerados adicionais.

Configuração inicial: 10 mil avaliações, seed 42, 30 grupos, 80 candidatos e até 8 trechos. Esses valores são de desenvolvimento e devem ser congelados antes do teste final. As respostas devem citar IDs de evidência e se abster quando o contexto for insuficiente.

### 3. Resultados

A auditoria inicial encontrou 720 registros sem texto e 9.445 duplicatas segundo a regra adotada, resultando em 691.363 avaliações válidas e únicas. Foi gerada uma amostra determinística de 10 mil registros. Essas contagens descrevem a preparação dos dados, não a qualidade do RAG.

Não há, por enquanto, resultados de avaliação humana de cobertura ou fidelidade. As métricas permanecerão ausentes até a anotação. Testes de software e testes de integração não serão apresentados como evidência de qualidade dos insights.

### 4. Conclusões

As conclusões serão redigidas após a execução e análise do experimento. Serão discutidos ganhos ou perdas de cobertura, sustentação das afirmações, custos e limitações: recorte de categoria, amostragem, subjetividade da anotação, agrupamentos não supervisionados, efeito do orçamento de contexto e variabilidade da inferência local.

---

Matrícula:

Pontifícia Universidade Católica do Rio de Janeiro

Pós-graduação em Inteligência Artificial Generativa e LLM
