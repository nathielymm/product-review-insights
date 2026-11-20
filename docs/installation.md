# Instalação e uso em outro computador

## Requisitos

- Git e acesso ao repositório privado para clonar.
- Python 3.11 ou superior com suporte a ambientes virtuais.
- [Ollama](https://ollama.com/download) instalado e ativo localmente.
- Internet durante a instalação e a preparação; espaço para os pacotes, All_Beauty (327 MB), encoder e Gemma 3 4B (aproximadamente 3,4 GB), além dos índices.
- Memória suficiente para executar Gemma 3 4B com janela de 8.192 tokens. O desempenho depende do computador; a aplicação não exige chave de API ou serviço pago.

As instruções usam os pacotes disponíveis para o sistema e registram suas versões na preparação. O arquivo `requirements.lock.txt` descreve o ambiente experimental, não é obrigatório para instalar a aplicação em outra plataforma.

## 1. Clonar e instalar

macOS/Linux:

```sh
git clone https://github.com/nathielymm/product-review-insights.git
cd product-review-insights
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Windows, no PowerShell (sem necessidade de ativar scripts):

```powershell
git clone https://github.com/nathielymm/product-review-insights.git
cd product-review-insights
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Nos comandos seguintes, no Windows substitua `python` por `.\.venv\Scripts\python.exe`.

## 2. Preparar os arquivos

Abra o Ollama. Se não houver serviço ativo, execute `ollama serve` em outro terminal. Mantenha o endpoint padrão `127.0.0.1:11434`.

Na raiz do projeto:

```sh
python scripts/setup_demo.py
```

O comando:

1. Confere o Ollama e baixa `gemma3:4b` pela API local caso ainda não esteja instalado.
2. Baixa o arquivo público All_Beauty de uma revisão fixa e confere tamanho e SHA-256. Um arquivo incompleto não é aceito como dataset pronto.
3. Seleciona os três identificadores de produto, omite identificadores de usuários e imagens, aplica redação heurística de e-mails/URLs/telefones, deduplica os textos e seleciona avaliações em inglês com pelo menos cinco palavras. A amostra tem limite de 1.000 avaliações por produto, por ordem de hash, sem seleção pela resposta do modelo.
4. Obtém o encoder MiniLM em revisão fixa, cria embeddings, índices FAISS e quatro agrupamentos dentro de cada produto.
5. Registra hashes dos arquivos, versões das bibliotecas e a versão/digest do modelo local em `artifacts/local-app/application.json`.

O download do encoder não executa código remoto do repositório de modelos. Dados são obtidos na fonte e mantidos localmente; o Git não distribui avaliações, modelos ou informações pessoais. A redação heurística não garante anonimização completa. Consulte as condições de uso e a documentação do [dataset oficial](https://amazon-reviews-2023.github.io/) e do [Gemma](https://ollama.com/library/gemma3).

O arquivo baixado fica em `data/raw/local-app/`; corpora, encoder, índices e manifesto ficam em `artifacts/local-app/`. A preparação não lê as anotações privadas nem altera os arquivos da execução experimental.

Ao repetir o comando após uma preparação concluída, ele confere a integridade e o runtime sem reconstruir os índices. Uma preparação interrompida pode ser retomada pelo mesmo comando, reaproveitando o download verificado. Se houver alteração de código, receita, bibliotecas ou runtime depois da preparação, a validação pode recusá-la; use um clone novo para uma nova preparação, preservando a anterior.

## 3. Iniciar e consultar

```sh
python scripts/serve_demo.py
```

Abra [http://127.0.0.1:8501](http://127.0.0.1:8501). Escolha um produto, um dos dois métodos e uma pergunta predefinida ou livre. As fontes ficam em inglês, e a apresentação da resposta é traduzida para português. Encerre com Ctrl+C; outra porta pode ser escolhida com `--port 8503`.

Depois da preparação, o encoder é carregado localmente e as avaliações não são enviadas a serviços externos: as chamadas de geração e tradução usam o Ollama em loopback. Não é necessário repetir os downloads a cada uso. Mantenha o serviço Ollama ativo.

## 4. Verificações

```sh
python -m pytest -q
```

Os testes usam entradas sintéticas e não exigem downloads, modelos ou arquivos privados. A preparação verifica os próprios hashes, e cada consulta confere que o runtime/modelo continua sendo o registrado.

O fluxo foi executado em um ambiente virtual novo no macOS arm64: instalação pelo `pyproject.toml`, download público verificado, construção dos três índices, 85 testes e consultas reais dos dois métodos nos três produtos. A interface também foi conferida no navegador. Os testes usaram um serviço Ollama local já instalado; o caminho de download de um modelo ausente tem teste de API simulada. As instruções Windows/Linux não foram executadas. Versões e contagens constam em [local-install-validation.json](local-install-validation.json).

## Uso da ferramenta e reprodução das métricas

O caminho acima permite usar a aplicação a partir do código e de fontes públicas. Os índices recém-construídos não são apresentados como os índices do experimento: as contagens podem diferir do recorte revisado, assim como versões e respostas ao vivo. O manifesto registra explicitamente essa separação.

Para conferir a configuração original e recalcular os resultados do TCC, siga [reproduction.md](reproduction.md). Essa tarefa exige os corpora e arquivos de anotação experimentais locais. Com esses insumos, a interface original pode ser aberta com `python scripts/serve_demo.py --frozen`; essa opção mantém as verificações estritas do experimento.

## Problemas comuns

| Mensagem/situação | Ação |
|---|---|
| Não foi possível acessar o Ollama | Abra o aplicativo ou execute `ollama serve`; confira a porta 11434. |
| Prepare os arquivos com `setup_demo.py` | Execute a preparação na raiz do projeto, com internet e Ollama ativo. |
| Falha no download | Confira conexão/espaço e execute a preparação novamente; downloads incompletos são descartados. |
| Checksum ou arquivo alterado | Não edite hashes para contornar a validação. Preserve a instalação e prepare um clone novo. |
| Porta 8501 ocupada | Use `python scripts/serve_demo.py --port 8503`. |
| Instalação sem wheel compatível | Use Python/arquitetura suportados pelas bibliotecas; instalações fora do ambiente validado precisam de conferência própria. |
