# Identificação de oportunidades de melhoria em produtos com RAG

Comparação entre RAG tradicional e RAG enriquecido por análise temática.

#### Aluna: Nathiely Laiane Moraes Macedo
#### Orientador(a): Leonardo Alfredo Forero Mendonza

Trabalho apresentado ao curso [Inteligência Artificial Generativa e LLM — PUC-Rio](https://ica.ele.puc-rio.br/cursos/ia-generativa-large-language-models/) como pré-requisito para conclusão de curso e obtenção de crédito na disciplina "PROJETO LLM".

[Link para o código](https://github.com/nathielymm/product-review-insights). 

### 1. Introdução

Este trabalho investiga como avaliações de consumidores podem apoiar a identificação de oportunidades de melhoria em produtos. Compara duas formas de selecionar evidências para um modelo de linguagem: similaridade com a pergunta e diversidade temática dentro de um mesmo produto, seguindo o princípio de RAG (Lewis et al., 2020).

O estudo utiliza 1.209 avaliações do arquivo fornecido como Amazon Reviews 2023 All_Beauty (Hou et al., 2024), distribuídas entre escova GranNaturals (613), shampoo Pure Body Naturals Argan (473) e máscara Bold Lash (123). Cada produto é analisado separadamente, preservando as condições e comparações presentes nos relatos.

### 2. Modelagem

O sistema usa embeddings do modelo `all-MiniLM-L6-v2`, do Sentence Transformers (Reimers; Gurevych, 2019), índice FAISS (Johnson; Douze; Jégou, 2017) e quatro agrupamentos MiniBatchKMeans por produto (Sculley, 2010). Para cada pergunta, cinco buscas por aspectos são combinadas por Reciprocal Rank Fusion (Cormack; Clarke; Büttcher, 2009), formando um ranking comum, deduplicado por avaliação:

- RAG tradicional: seleciona as primeiras oito avaliações do ranking.
- RAG temático: seleciona representantes dos agrupamentos disponíveis e completa as oito posições pelo mesmo ranking.

Ambos usam Gemma 3 4B (Gemma Team, 2025) local via Ollama, com os mesmos parâmetros de geração. As respostas são geradas em inglês e traduzidas para português apenas na apresentação, mantendo as fontes acessíveis.

A avaliação compreende seis perguntas por produto, 36 respostas principais e 24 repetições diagnósticas separadas. A rubrica considera cobertura, fidelidade, suporte das citações, propostas de melhoria e limites das inferências comerciais. Foram registrados tempos de execução e tokens. A anotação assistida teve revisão humana das interpretações de 12 respostas, sem avaliação independente.

#### Como executar

Pré-requisitos: Git, Python 3.11 ou superior e [Ollama](https://ollama.com/download). Os comandos abaixo usam macOS/Linux; as instruções para Windows estão no [guia de instalação](docs/installation.md).

```sh
git clone https://github.com/nathielymm/product-review-insights.git
cd product-review-insights
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Com o Ollama aberto, ou `ollama serve` em outro terminal:

```sh
python scripts/setup_demo.py
python scripts/serve_demo.py
```

Abra [http://127.0.0.1:8501](http://127.0.0.1:8501), escolha o produto, o método e a pergunta. A resposta apresenta os achados, sugestões e fontes.

A primeira preparação baixa o All_Beauty de uma revisão pública fixa, o encoder e, se necessário, o Gemma 3 4B. Em seguida, seleciona avaliações por produto e cria os índices e agrupamentos locais. Requer internet e espaço para os modelos; nas próximas utilizações, basta iniciar Ollama e a interface. Dados e modelos não são versionados.

Essa preparação permite usar a ferramenta sem os arquivos privados da pesquisa. Ela cria seus próprios corpora e registra as versões utilizadas; não substitui o recorte anotado nem recalcula os resultados abaixo. O [guia de reprodução](docs/reproduction.md) explica a conferência do experimento e os insumos necessários para reproduzir suas métricas.

Para executar os testes, sem baixar dados ou chamar o modelo:

```sh
python -m pytest -q
```

### 3. Resultados

| Indicador | RAG tradicional | RAG temático |
|---|---:|---:|
| Cobertura de conteúdo com apoio e citação | 12,50% | 18,75% |
| Fidelidade ao contexto | 85,33% | 80,95% |
| Suporte das próprias citações | 80,84% | 78,83% |
| Mediana da geração em inglês, com verificações | 5,92 s | 5,46 s |

As médias de qualidade atribuem pesos iguais às perguntas elegíveis dentro de cada produto e depois aos produtos. A cobertura é relativa à referência parcial construída, não a todos os temas do corpus. O temático ampliou a cobertura na escova e na máscara, com empate no shampoo. O tradicional apresentou maior fidelidade média. Não houve vantagem uniforme entre os produtos e critérios.

Os dois métodos tiveram dificuldades para preservar qualificações e contrastes completos e fundamentar propostas de melhoria. As 60 gerações em inglês e 36 traduções passaram nas verificações de formato, sem cortes ou erros de chamada; isso não comprova correção semântica.

Consulte os [resultados detalhados e denominadores](docs/product-evaluation.v2-results.md) e a [discussão dos achados](docs/discussion-and-conclusions.v2.md).

### 4. Conclusões

A diversidade temática ampliou a cobertura média, mas não assegurou maior fidelidade. A identificação de oportunidades exige preservar o vínculo entre cada achado, sua fonte e as condições relatadas. As sugestões produzidas são hipóteses de melhoria, sem comprovação de causalidade ou impacto em vendas.

As conclusões se restringem aos três produtos, à referência parcial e à anotação assistida com revisão humana parcial. Os agrupamentos são exploratórios, a equivalência das traduções não foi integralmente certificada e a procedência exata do Parquet experimental em relação à fonte oficial permanece uma limitação. Os custos medidos abrangem tempo e tokens, sem medição de CPU, memória, energia ou custo monetário. Avaliação independente e ampliação das referências são caminhos para aprofundar os resultados.

### Referências

- LEWIS et al. (2020). [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401).
- REIMERS; GUREVYCH (2019). [Sentence-BERT](https://aclanthology.org/D19-1410/). Encoder utilizado: [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2).
- JOHNSON; DOUZE; JÉGOU (2017). [Billion-scale similarity search with GPUs — FAISS](https://arxiv.org/abs/1702.08734).
- SCULLEY (2010). [Web-Scale K-Means Clustering](https://doi.org/10.1145/1772690.1772862).
- CORMACK; CLARKE; BÜTTCHER (2009). [Reciprocal Rank Fusion](https://doi.org/10.1145/1571941.1572114).
- GEMMA TEAM (2025). [Gemma 3 Technical Report](https://arxiv.org/abs/2503.19786).
- HOU et al. (2024). [Bridging Language and Items for Retrieval and Recommendation — Amazon Reviews 2023](https://arxiv.org/abs/2403.03952).

---

Matrícula: 252.100.329

Pontifícia Universidade Católica do Rio de Janeiro

Pós-graduação em Inteligência Artificial Generativa e LLM
