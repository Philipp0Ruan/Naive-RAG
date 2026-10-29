# Resumo de desenvolvimento — Naive RAG

Atualizado em 29/10/2026.

## Objetivo

Responder às cinco perguntas sobre Os Sertões usando os trechos recuperados diretamente por busca por similaridade.

Repositório: https://github.com/Philipp0Ruan/Naive-RAG

Este projeto tem seu próprio código, notebook, dados, resultados e checklist. Pode ser desenvolvido e executado dentro desta pasta, sem importar código de outro repositório.

## Situação atual

A preparação inicial está concluída. O arquivo Python apresenta o roteiro e lê as cinco perguntas; o notebook importa essa base e também lê as perguntas. A recuperação, a geração com LLM e a avaliação final ainda precisam ser implementadas. Ainda não há respostas geradas nem resultados do experimento.

## Arquivos para continuar o trabalho

- [naive_rag.py](naive_rag.py): base Python da implementação.
- [notebooks/naive_rag.ipynb](notebooks/naive_rag.ipynb): execução das etapas no Jupyter.
- [evaluation/perguntas.json](evaluation/perguntas.json): perguntas Q1 a Q5.
- [CHECKLIST_EXECUCAO.md](CHECKLIST_EXECUCAO.md): controle local detalhado das tarefas, ignorado pelo Git.
- [README.md](README.md): apresentação do projeto e instruções de uso.
- `data/`: PDF e dados extraídos, mantidos localmente.
- `storage/`: índices e dados persistidos, a criar durante a implementação.
- `results/`: respostas e avaliações, a produzir durante a execução.

## Fluxo desta abordagem

```text
PDF → texto com páginas → trechos → embeddings → índice vetorial → busca por similaridade → contexto → resposta com fontes
```

A resposta deve usar os trechos retornados pela busca por similaridade, sem uma etapa adicional de expansão para pais ou reranking.

## Etapas para concluir

1. Definir o ambiente, as dependências, o modelo de embeddings e o LLM.
2. Baixar o livro, registrar o hash, extrair o texto por página e conferir a limpeza.
3. Separar o texto em trechos com identificadores, páginas e sobreposição definida.
4. Gerar embeddings, criar o índice e validar sua persistência e recarga.
5. Recuperar os k trechos mais próximos de cada pergunta e montar o contexto.
6. Gerar respostas em português com páginas e indicação de evidência insuficiente.
7. Executar as cinco perguntas e revisar as evidências no PDF.
8. Validar o pipeline completo pelo Python e pelo notebook, registrar resultados e atualizar o README.

## Próximo passo

Começar pela seção **1. Ambiente e escolhas** do checklist. Definir bibliotecas, modelos e configuração antes de implementar a leitura e a recuperação do livro. O Python 3.12 já foi usado na verificação inicial; o ambiente virtual, as dependências de RAG e a instalação do Jupyter ainda precisam ser preparados.

Manter as funções na base Python e usá-las no notebook, com os mesmos parâmetros, para que os dois formatos produzam resultados equivalentes.

## Perguntas que precisam ser respondidas

- **Q1:** Qual é a visão de Euclides da Cunha sobre o ambiente natural do sertão nordestino e como ele influencia a vida dos habitantes?
- **Q2:** Quais são as principais características da população sertaneja descritas por Euclides da Cunha? Como ele relaciona essas características com o ambiente em que vivem?
- **Q3:** Qual foi o contexto histórico e político que levou à Guerra de Canudos, segundo Euclides da Cunha?
- **Q4:** Como Euclides da Cunha descreve a figura de Antônio Conselheiro e seu papel na Guerra de Canudos?
- **Q5:** Quais são os principais aspectos da crítica social e política presentes em "Os Sertões"? Como esses aspectos refletem a visão do autor sobre o Brasil da época?

## Critérios de conclusão

O projeto estará concluído quando o Python e o notebook executarem o pipeline completo, as cinco respostas estiverem registradas com trechos e páginas verificáveis, o índice puder ser recarregado e o README explicar uma execução reproduzível.

Registrar configurações, tempos e tokens/custo quando disponíveis. Apontar evidências insuficientes e limitações. Separar o texto de Euclides dos materiais editoriais do PDF e distinguir a página física do PDF da página impressa.

Uma comparação futura poderá usar os resultados dos outros experimentos. Isso não exige uma pasta de projeto geral nem dependências entre os repositórios.

## Fonte do livro

[PDF de Os Sertões](https://fundar.org.br/wp-content/uploads/2021/06/os-sertoes.pdf).

Ao terminar cada etapa, atualizar este resumo com a situação real e marcar no checklist apenas o que tiver sido verificado.
