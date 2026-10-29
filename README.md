# Naive RAG — Os Sertões

Um experimento para responder às cinco perguntas do desafio sobre **Os Sertões**, de Euclides da Cunha. O programa extrai o texto do PDF, divide a obra em trechos, encontra os mais próximos da pergunta e entrega esse contexto à OpenAI.

A implementação está em [naive_rag.py](naive_rag.py). O [Jupyter Notebook](notebooks/naive_rag.ipynb) usa as mesmas funções e a mesma configuração.

## O que está implementado

- Download do PDF e conferência do SHA-256 da edição.
- Extração por página, limpeza de margens e correção de palavras hifenizadas em quebras de linha.
- Trechos com sobreposição, fonte, página do PDF e página impressa.
- Embeddings locais com `intfloat/multilingual-e5-small`, em revisão fixa.
- Busca por similaridade de cosseno, sem expansão para pais e sem reranking.
- Persistência dos embeddings e metadados, com conferência ao recarregar.
- Geração pela Responses API da OpenAI, orientada a responder com base nos trechos e citar páginas.
- Execução das cinco perguntas, com exportação em JSON e Markdown.
- Testes locais que não fazem chamadas pagas.

Os testes atuais usam **simulação**, conforme combinado. O comando `simular` exercita as cinco perguntas com documentos sintéticos, vetores programados e um cliente falso de LLM. Não lê credenciais, não baixa o livro ou modelos e bloqueia conexões de rede durante o cenário. Os textos fictícios não avaliam a qualidade das respostas sobre a obra.

A geração real com OpenAI fica para depois da aprovação. Os relatórios anteriores no modo `somente_busca` contêm evidências recuperadas, sem respostas de LLM. O andamento está em [resume.md](resume.md).

## Preparar o ambiente

Use **Python 3.12**. No PowerShell, dentro desta pasta:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install torch==2.7.1 --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements-notebook.txt
Copy-Item .env.example .env
```

Se o `.env` já existir, mantenha o arquivo atual. Depois da aprovação para os testes reais, preencha nele:

```dotenv
OPENAI_API_KEY=sua_chave_local
OPENAI_MODEL=gpt-5-mini
OPENAI_TEMPERATURE=
```

O `.env` é ignorado pelo Git. Deixe a temperatura vazia para usar o padrão do modelo; alguns modelos não aceitam uma temperatura personalizada. O modelo de geração pode ser trocado por outro disponível na sua conta. O modelo efetivamente retornado pela API fica registrado nos resultados.

A instalação e a primeira indexação precisam de internet. O PDF tem cerca de 8 MB e o modelo de embeddings exige um download maior. Depois de baixados, o índice e a busca funcionam localmente. A geração continua precisando de acesso à OpenAI e pode consumir créditos da sua conta.

## Executar a simulação em Python

```powershell
.\.venv\Scripts\python.exe naive_rag.py simular
```

A simulação salva `results/simulacao.json` e `results/simulacao.md`, com avisos explícitos e `simulado: true`. A busca por cosseno, a montagem do contexto, a recarga do índice, as citações e a exportação usam as funções de produção; os dados e as dependências de geração são de teste. O cenário sem evidência verifica que a geração não é tentada. Não são medidos tokens, custo nem qualidade de um LLM real.

## Comandos para a execução real, depois da aprovação

```powershell
# Baixa o livro, cria o índice ou recarrega um índice compatível
.\.venv\Scripts\python.exe naive_rag.py indexar

# Busca trechos sem chamar a OpenAI
.\.venv\Scripts\python.exe naive_rag.py buscar "Como o ambiente influencia a vida do sertanejo?"

# Responde uma pergunta usando os trechos recuperados
.\.venv\Scripts\python.exe naive_rag.py responder "Como Euclides descreve Antônio Conselheiro?"

# Executa e exporta as cinco perguntas do desafio
.\.venv\Scripts\python.exe naive_rag.py avaliar

# Executa somente a recuperação das cinco perguntas, sem chave de API
.\.venv\Scripts\python.exe naive_rag.py avaliar --somente-busca
```

As consultas precisam de um índice criado previamente. Se alterar tamanho dos trechos, revisão do embedding ou limites do corpus, reconstrua-o:

```powershell
.\.venv\Scripts\python.exe naive_rag.py indexar --refazer
```

O script encontra dados e configurações a partir da sua própria localização; pode ser chamado por caminho completo mesmo fora da pasta do projeto.

## Executar no Jupyter

```powershell
.\.venv\Scripts\python.exe -m ipykernel install --prefix .venv --name naive-rag --display-name "Python (Naive RAG)"
.\.venv\Scripts\python.exe -m jupyterlab notebooks/naive_rag.ipynb
```

Selecione o kernel **Python (Naive RAG)** e execute as células em ordem. No VS Code, também é possível selecionar diretamente o Python da `.venv`.

O notebook começa com `MODO = "simulado"` e pode ser executado inteiro sem chave, PDF ou download de modelos. Todas as saídas da simulação são identificadas como fictícias.

Depois da aprovação, `MODO = "somente_busca"` permite usar a busca real sem geração, e `MODO = "real"` habilita as chamadas à OpenAI com o `.env` configurado. Nenhum teste real é agendado automaticamente.

## Configuração do experimento

Os parâmetros estão em [config.json](config.json):

| Parâmetro | Valor inicial |
| --- | --- |
| Corpus | Páginas físicas 33 a 653 do PDF |
| Embedding | `intfloat/multilingual-e5-small` |
| Revisão do embedding | `614241f622f53c4eeff9890bdc4f31cfecc418b3` |
| Trecho | Até 350 tokens do tokenizer do E5 |
| Sobreposição | 50 tokens, dentro da mesma página |
| Busca | Oito trechos por similaridade de cosseno |
| Contexto | Até 16.000 caracteres, com trechos inteiros |
| Limite de saída da OpenAI | 4.096 tokens |
| Limiar de similaridade | Desativado; não foi calibrado |

Os textos recebem o prefixo `passage: ` e as perguntas, `query: `, conforme as instruções do E5. O programa confere se cada trecho cabe no modelo, incluindo o prefixo. Os embeddings são normalizados, e a busca calcula o produto escalar com NumPy. Para o tamanho deste livro, um índice exato é suficiente e facilita conferir o que foi recuperado.

O orçamento de contexto é medido em caracteres, não em tokens do LLM. Similaridade não representa uma probabilidade de a resposta estar correta.

## Corpus e páginas

O PDF tem 658 páginas físicas. O corpus começa na nota preliminar de Euclides, na página PDF 33, e inclui as notas do autor à segunda edição até a página PDF 653. Apresentação, prefácio, sumário e créditos editoriais ficam de fora.

Nesta edição, a página impressa corresponde à página física do PDF menos 30. Por exemplo, a descrição do sertanejo na página impressa 115 está na página PDF 145. Essa regra vale para a edição identificada pelo hash do `config.json`.

Os trechos conservam as duas referências. A resposta usa `[PDF p. N]` para facilitar a conferência no arquivo. A limpeza não resolve todos os detalhes de diagramação: capitulares e algumas ligaturas podem deixar marcas na extração.

As notas de rodapé do miolo permanecem no texto extraído. Algumas são editoriais, identificadas por `(PRP)`; o prompt orienta o modelo a não atribuí-las a Euclides. A distinção também deve ser conferida na revisão das respostas.

## Resultados e avaliação

Cada lote produz arquivos em `results/`, com perguntas, respostas quando geradas, trechos recuperados, trechos usados no contexto, páginas, similaridades, configurações, versões e tempos. O uso de tokens é registrado quando a API o fornece. O custo fica como `null`: o projeto não estima preços nem apresenta ausência de medição como custo zero.

A conferência automática identifica páginas citadas fora do contexto. Ela não verifica se uma afirmação está sustentada pelo trecho. Essa revisão é manual, seguindo [evaluation/rubrica.md](evaluation/rubrica.md).

As cinco perguntas originais estão em [evaluation/perguntas.json](evaluation/perguntas.json). Perguntas interpretativas podem exigir evidências espalhadas pelo livro; oito trechos nem sempre cobrem todos os pontos. O prompt pede ao modelo que declare as limitações, mas isso também precisa ser avaliado.

## Validação local

A suíte local tem 15 testes, incluindo integração e falhas simuladas. Os arquivos de teste não são distribuídos pelo Git. A simulação pode ser executada com `python naive_rag.py simular`.

## Arquivos

```text
naive_rag.py                  implementação e comandos
simulacao.py                  cenário offline de integração
config.json                   parâmetros do experimento
notebooks/naive_rag.ipynb      experimento no Jupyter
evaluation/perguntas.json      cinco perguntas
evaluation/rubrica.md          critérios de revisão
results/                      relatórios do experimento
resume.md                     andamento deste projeto
```

O PDF, o índice, o cache do modelo, a `.venv`, o `.env` e o `CHECKLIST_EXECUCAO.md` ficam apenas no computador e são ignorados pelo Git. Parent RAG e Rerank RAG são projetos separados, sem dependências de código entre os repositórios.

## Referências

- [PDF de Os Sertões](https://fundar.org.br/wp-content/uploads/2021/06/os-sertoes.pdf).
- [Desafio e solução de referência da Rocketseat](https://github.com/rocketseat-education/ia-para-devs/tree/master/Desafio%20RAG).
- [Instruções do multilingual-e5-small](https://huggingface.co/intfloat/multilingual-e5-small).
- [Sentence Transformers](https://sbert.net/docs/quickstart.html).
- [Extração de texto com pypdf](https://pypdf.readthedocs.io/en/stable/user/extract-text.html).
- [SDK Python da OpenAI e Responses API](https://developers.openai.com/api/reference/python).

## Docker

Dentro deste repositório, execute o cenário simulado:

```powershell
docker compose build rag
docker compose run --rm rag
```

Para abrir o Jupyter:

```powershell
docker compose up notebook
```

O Jupyter fica em http://localhost:8888; use o token informado no terminal. O notebook começa com `MODO = "simulado"`. A simulação não precisa de chave, PDF nem download de modelos. Os relatórios são salvos localmente em `results/`.

A imagem padrão usa o alvo leve `simulation`. O alvo `runtime` instala também os modelos locais via dependências PyTorch/Sentence Transformers; o download dos pesos acontece na primeira indexação. Depois da aprovação para os testes reais:

```powershell
Copy-Item .env.example .env
# Preencha a chave somente no .env local.
docker compose --profile real build real
docker compose --profile real run --rm real python naive_rag.py indexar
docker compose --profile real run --rm real
```

Mantenha o `.env` existente se ele já estiver configurado. A imagem não inclui credenciais, dados locais, índices, testes ou relatórios. As pastas de dados, cache, índice e resultados são montadas como volumes na execução real.

O Jupyter padrão usa a imagem simulada. Para um notebook com modelos reais, depois da aprovação:

```powershell
docker compose --profile real run --rm -p 127.0.0.1:8888:8888 -v ./notebooks:/app/notebooks real python -m jupyterlab --ip=0.0.0.0 --port=8888 --no-browser --ServerApp.root_dir=/app
```

## Versionamento

Os testes e relatórios ficam apenas no computador, ignorados pelo Git e pelo contexto Docker. O comando `simular` faz parte da aplicação e permite conferir o fluxo a partir de um clone novo. Os commits novos usam prefixos como `feat:`, `fix:`, `chore:` e `docs:`.
