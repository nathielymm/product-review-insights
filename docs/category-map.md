# Mapeamento exploratório de categorias — 8 de novembro de 2026

Etapa posterior: a usuária propôs comparar conjuntos compacto, intermediário e variado. A exploração atual está em [Candidatos a três condições de variedade](diversity-candidates.md). O mapeamento de categorias abaixo permanece como etapa de triagem, não como recorte fechado.

## Resultado e alcance

Há alternativas para estudar vários produtos de uma mesma categoria. A proposta anterior de um shampoo e um difusor não está fechada e foi substituída por esta exploração. Nenhum índice ou experimento final foi alterado.

O arquivo de metadados oficial tem 112,590 registros; todos os 112,496 IDs com avaliações válidas encontram correspondência nele. O total auditado permanece em 691,363 avaliações válidas e únicas.

O campo categories está vazio nos 112,590 registros. main_category distingue apenas All Beauty (112.135) e Premium Beauty (455). Conferimos também details: há atributos como marca e formato, mas não encontramos Best Sellers Rank com uma taxonomia aproveitável. Os títulos oficiais permitem uma classificação exploratória; as categorias desta análise não são subcategorias oficiais recuperadas do arquivo.

## Método e limites

A classificação usa regras explícitas nos títulos do catálogo, sem usar respostas dos RAGs nem temas gerados pelo modelo. Casos sem correspondência ou com múltiplas categorias ficam separados. A revisão de títulos dos produtos elegíveis em seis grupos corrigiu falsos encaixes: frascos vazios para shampoo; óleo para barba chamado conditioner; suportes, tapetes e limpadores chamados makeup brush; moldes de esmalte; kits de cílios que mencionam delineador. A regra refinada classifica 32,618 IDs em um único grupo (29.0%); 77,881 ficam sem classificação e 1,997 ficam ambíguos.

A cobertura limitada impede apresentar isto como um censo definitivo por categoria. As contagens são dos produtos identificados pelas regras atuais e podem mudar com revisão de títulos ou metadados. Títulos e atributos podem estar incorretos ou desatualizados; não validam automaticamente a consistência das avaliações associadas a cada ID.

Para triagem, consideramos produto elegível aquele com pelo menos 100 avaliações válidas e únicas e pelo menos 30 avaliações com 20 ou mais palavras. O comprimento é uma aproximação de material descritivo, não uma medida de qualidade. Examinamos ainda os limiares 50 e 200. Esses cortes são pragmáticos e não demonstram suficiência estatística ou saturação temática.

As notas são agregadas com a mesma regra de deduplicação da auditoria: texto normalizado/redigido por parent_asin, menor nota em duplicatas conflitantes. As contagens ainda não filtram idioma; o tamanho do corpus final poderá diminuir. Não foram removidos produtos por apresentarem opiniões positivas ou negativas.

## Comparação de categorias

| Grupo inferido dos títulos | IDs identificados no grupo | Avaliações desses IDs | IDs elegíveis (≥100 avaliações e ≥30 textos com ≥20 palavras) | Avaliações dos IDs elegíveis |
|---|---:|---:|---:|---:|
| Desodorantes | 921 | 7,964 | 16 | 2,851 |
| Cílios magnéticos e kits com delineador | 658 | 8,978 | 14 | 2,606 |
| Pincéis de maquiagem | 687 | 6,353 | 14 | 2,249 |
| Esmaltes | 2,135 | 12,308 | 13 | 2,450 |
| Escovas e pentes para cabelo | 2,243 | 16,210 | 11 | 3,765 |
| Perfumes e fragrâncias | 2,158 | 10,169 | 11 | 1,722 |
| Shampoos | 956 | 6,211 | 7 | 1,758 |
| Condicionadores | 774 | 5,083 | 5 | 1,087 |
| Máscaras para cílios | 747 | 6,061 | 5 | 1,145 |
| Difusores para secador | 47 | 2,304 | 3 | 1,681 |
| Máscaras capilares | 68 | 1,188 | 3 | 807 |

Os grupos amplos ainda podem reunir tipos diferentes. Exemplos: pincéis individuais e kits, esmaltes tradicionais e gel, shampoo em barra e em frasco. Para decidir o recorte, precisamos estreitar também a função/formato, sem nos limitar apenas ao nome genérico da categoria.

## Subgrupos candidatos mais comparáveis

| Recorte por título, entre os IDs elegíveis | IDs | Avaliações | Participação do maior ID nas avaliações desse recorte |
|---|---:|---:|---:|
| Máscaras para cílios | 5 | 1,145 | 25.6% |
| Kits de pincéis de maquiagem | 9 | 1,521 | 35.4% |
| Esmaltes de cor sem indicação de gel, magnético ou base/top coat | 8 | 1,623 | 32.5% |
| Desodorantes (formatos variados) | 16 | 2,851 | 12.6% |
| Cílios magnéticos e kits com delineador | 14 | 2,606 | 12.0% |
| Shampoos (inclui barras) | 7 | 1,758 | 47.7% |
| Shampoos sem indicação de barra no título | 5 | 1,436 | 58.4% |
| Condicionadores (enxágue, leave-in e barra) | 5 | 1,087 | 40.5% |
| Difusores para secador | 3 | 1,681 | 78.1% |

Esses subgrupos se sobrepõem: por exemplo, os shampoos sem indicação de barra fazem parte do grupo shampoos. Não somar suas contagens. IDs parent_asin também podem representar cores, embalagens ou versões da mesma família; contagem de IDs não equivale a contagem de modelos ou marcas independentes.

## Leitura para a escolha

1. Máscaras para cílios: cinco IDs, 1.145 avaliações e 581 textos com pelo menos 20 palavras. É um candidato compacto e funcionalmente coerente; o maior ID responde por 25,6% do material. Podemos investigar aplicação, resultado percebido, duração e embalagem, após validar que os relatos de fato cobrem essas dimensões. Há dois títulos da mesma marca; faltam alguns atributos de marca/formato no catálogo.
2. Kits de pincéis: nove IDs, 1.521 avaliações e 593 textos com pelo menos 20 palavras. Adequado para investigar características físicas, experiência de uso e composição dos kits. Há pares de títulos aparentemente diferenciados por cor (VANDER LIFE e Soobest), que devem ser tratados como potenciais variantes da mesma família, não como nove modelos independentes. O maior ID tem 35,4% das avaliações.
3. Esmaltes de cor: o refinamento pelo título encontra oito IDs e 1.623 avaliações. Há lotes e conjuntos de cores. Um registro tem Item Form=Gel apesar de não ter indicação de gel no título; precisa de revisão antes de chamar esse conjunto de esmaltes tradicionais. Não misturar produtos com modos de aplicação diferentes sem declarar isso.
4. Desodorantes: 16 IDs e 2.851 avaliações elegíveis, com bastante material descritivo. Porém nove IDs têm marca Lume nos atributos, e os formatos incluem stick, creme, roll-on e aerosol. Precisamos controlar famílias, formatos e concentração de marca. Relatos de desconforto não permitem conclusões clínicas.
5. Cílios magnéticos: 14 IDs e 2.606 avaliações elegíveis. Dois títulos descrevem fixação por ímãs sem delineador; os demais mencionam kits com delineador. Separar esses mecanismos antes de comparar vários produtos. Há atributos de marca discordantes em alguns títulos, reforçando a necessidade de revisão.
6. Shampoos: sete IDs elegíveis e 1.758 avaliações. Ao retirar títulos de barras, restam cinco IDs e 1.436 avaliações, mas um único ID concentra 58,4% desse material. Isso favorece uma amostragem equilibrada por produto, preservando a distribuição de notas dentro de cada um, caso esse seja o recorte escolhido. A indicação de líquido ainda precisa de validação: os atributos são incompletos e um Item Form está registrado como Oil.

Difusores têm apenas três IDs acima do corte e 78,1% das avaliações desses três vêm de um só ID. São úteis como estudo de caso, mas menos atraentes para o desenho de vários produtos que estamos discutindo. Condicionadores têm cinco IDs elegíveis, mas misturam enxágue, leave-in e barra; o volume não basta para garantir comparabilidade.

Minha sugestão é aprofundar primeiro máscaras para cílios e kits de pincéis, mantendo desodorantes e esmaltes como alternativas de maior variedade. São candidatos para inspeção, não uma escolha final. A etapa seguinte deve revisar famílias/variantes, idiomas, consistência das avaliações e diversidade temática em uma amostra determinística de cada candidato, sem observar qual método de RAG se sai melhor.

## Sensibilidade ao corte de volume

| Grupo | IDs com ≥50 avaliações | IDs com ≥100 avaliações | IDs com ≥200 avaliações |
|---|---:|---:|---:|
| Desodorantes | 32 | 16 | 5 |
| Cílios magnéticos e kits com delineador | 36 | 14 | 5 |
| Pincéis de maquiagem | 26 | 14 | 2 |
| Esmaltes | 31 | 13 | 3 |
| Shampoos | 16 | 7 | 2 |
| Máscaras para cílios | 22 | 5 | 3 |

Esta tabela considera somente volume; a coluna de elegibilidade acima acrescenta o mínimo de textos com 20 palavras. Diminuir o corte aumenta a variedade de IDs, mas reduz a evidência disponível por produto. Um único limiar não estabelece qual desenho é melhor.

## Reprodução, rastreabilidade e arquivos

```sh
.venv/bin/python scripts/map_categories.py
.venv/bin/python scripts/shortlist_categories.py
.venv/bin/python -m pytest -q
```

A classificação está em configs/category-rules.json; as regras dos subgrupos, em configs/category-shortlist-rules.json; os IDs candidatos e suas contagens, em configs/category-cohorts.draft.json. O resumo agregado está em docs/category-map-summary.json. Títulos, atribuições por produto, arquivos brutos e exemplos permanecem em data/ e results/, fora do Git.

Os 17 testes passaram, incluindo deduplicação, união com catálogo, ausência/ambiguidade de categorias e regressões contra acessórios classificados como produtos. Os totais de avaliações e produtos das categorias reconciliam com a auditoria. Nenhuma métrica de qualidade de RAG foi calculada nesta exploração.

Fonte oficial dos metadados: https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023/resolve/2b6d039ed471f2ba5fd2acb718bf33b0a7e5598e/raw_meta_All_Beauty/full-00000-of-00001.parquet

SHA-256 dos metadados: 14815cf1312a0d847364866e6876c8c73738993469067242870774c372c04387. Verificado contra o objeto LFS publicado no repositório oficial.

SHA-256 das avaliações fornecidas: b40ae565f1073e0b4960e2f424fe0c82f3d270b7c4d00bc9272ddd6a8b7411d7.

O cruzamento integral de IDs fortalece a compatibilidade do Parquet fornecido com All_Beauty; não comprova, por si só, identidade byte a byte com o arquivo oficial de avaliações. Origem e condições de redistribuição continuam documentadas como pendências. Nenhum dado bruto ou texto de avaliação foi versionado.
