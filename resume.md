# Resumo de desenvolvimento — Naive RAG

Atualizado em 29/10/2026.

## Objetivo

Responder às cinco perguntas sobre Os Sertões com um Naive RAG: recuperar trechos por similaridade e usá-los diretamente como contexto de geração, sem pais nem reranking.

Repositório: https://github.com/Philipp0Ruan/Naive-RAG

## Situação atual

O pipeline está implementado em `naive_rag.py` e no notebook que importa essa base. Em uma execução anterior, a extração, a indexação, a busca e a exportação foram verificadas com o livro real. A integração de geração com a OpenAI está implementada. Por orientação do usuário, a validação atual será apenas simulada; a geração real fica adiada até a aprovação. A simulação usa documentos fictícios, vetores programados e um cliente de LLM falso, sem acessar credenciais nem a rede.

O projeto tem ambiente próprio em `.venv`, JupyterLab instalado e kernel `Python (Naive RAG)`. Os 15 testes locais passaram, e a conferência de dependências não encontrou incompatibilidades.

## O que já foi verificado

- PDF com 658 páginas físicas, identificado por SHA-256 no `config.json`.
- Corpus nas páginas PDF 33 a 653: 620 páginas com texto, da nota preliminar às notas de Euclides à segunda edição.
- Exclusão de apresentação, prefácio, sumário e créditos editoriais externos ao corpus.
- Limpeza de margens e hifenização, conferida em páginas do início, meio e fim e nas três partes da obra.
- Índice com **1.176 trechos**, embeddings de **384 dimensões** e revisão fixa do E5.
- Janelas de 350 tokens e 50 de sobreposição, dentro de cada página.
- Busca exata por cosseno, com oito candidatos e limite de 16.000 caracteres de contexto.
- Persistência e recarga do índice, com verificação de configuração e integridade dos embeddings.
- Recuperação e exportação das cinco perguntas pelo Python, sem chamada de geração.
- Notebook executado do início ao fim em kernel novo no modo de recuperação.
- Testes de limpeza, sobreposição, contexto, busca, índice alterado, credenciais e montagem da chamada à OpenAI.

Os relatórios de recuperação não são respostas de LLM nem demonstram, por si, qualidade final das respostas. A revisão semântica permanece pendente.

## Validação simulada

O comando `simular` executa Q1 a Q5 com o mesmo fluxo de busca, contexto, geração e exportação, usando fixtures. Um cenário adicional sem evidência impede a geração. Também são simuladas falhas de autenticação, limite da API, conexão e respostas vazias/incompletas.

O notebook usa `MODO = "simulado"` por padrão. Os relatórios têm `simulado: true`, `api_real_executada: false` e tokens/custo como `null`. Eles não são respostas reais sobre o livro.

## Arquivos para continuar

- [naive_rag.py](naive_rag.py): implementação e comandos `indexar`, `buscar`, `responder` e `avaliar`.
- [notebooks/naive_rag.ipynb](notebooks/naive_rag.ipynb): experimento passo a passo, com saídas simuladas por padrão.
- [simulacao.py](simulacao.py): cenário offline e dependências simuladas.
- [results/simulacao.json](results/simulacao.json): execução simulada das cinco perguntas.
- [config.json](config.json): parâmetros, corpus, hash e revisão do embedding.
- [.env.example](.env.example): campos para a configuração local da OpenAI.
- [evaluation/perguntas.json](evaluation/perguntas.json): perguntas Q1 a Q5.
- [evaluation/rubrica.md](evaluation/rubrica.md): critérios de revisão das respostas.
- [results/recuperacao-inicial.json](results/recuperacao-inicial.json): evidências e medições da primeira execução pelo Python.
- [results/recuperacao-inicial.md](results/recuperacao-inicial.md): leitura das evidências por pergunta.
- [README.md](README.md): instalação, execução e limitações.
- `CHECKLIST_EXECUCAO.md`: checklist pessoal detalhado, ignorado pelo Git.

## Próximo passo

Por enquanto, usar apenas `python naive_rag.py simular` e os testes locais. A execução real só será retomada depois da aprovação do usuário, prevista para a noite se houver autorização. Nenhuma chamada à OpenAI foi feita e não há execução automática agendada.

Depois da aprovação:

1. Preencher `OPENAI_API_KEY` no `.env` local. Não colocar a chave no chat, no notebook ou no GitHub.
2. Executar `.\.venv\Scripts\python.exe naive_rag.py avaliar`.
3. No notebook, mudar `MODO = "real"` e executar as células de geração e avaliação.
4. Conferir as cinco respostas no PDF, seguindo a rubrica.
5. Testar uma pergunta sem evidência na obra e verificar a resposta do LLM real.
6. Registrar notas, limitações, uso de tokens e comparabilidade entre os dois formatos. Atualizar este resumo e o checklist somente com resultados verificados.

## Limitações já observadas

A primeira busca retorna trechos relacionados ao tema, mas nem sempre reúne todos os pontos de perguntas amplas. Alguns resultados são continuações curtas de páginas e podem trazer pouca informação isoladamente. Aumentar a similaridade ou a quantidade de candidatos não prova melhoria de qualidade.

As notas de rodapé do miolo continuam no texto; as notas editoriais assinadas `(PRP)` devem ser distinguidas do texto de Euclides. O prompt explicita essa distinção. Capitulares e algumas ligaturas também podem deixar marcas da diagramação.

O limite de contexto é em caracteres. Não foi calibrado um limiar de similaridade para rejeitar perguntas sem evidência. A conferência de citação valida páginas, sem provar a sustentação de cada afirmação.

Os campos de custo ficam como `null` enquanto não houver uma medição válida. As execuções registram as versões de bibliotecas e o modelo retornado pela API; o alias do modelo de geração pode mudar entre datas.

## Critério de conclusão

A implementação está validada por testes simulados. Concluir o desafio ainda exige, depois da aprovação, a geração real das cinco respostas, a revisão das evidências e a execução do fluxo completo nos dois formatos. A implementação e a recuperação já estão disponíveis; essas etapas finais ainda não foram concluídas.

Todo o desenvolvimento deste projeto fica nesta pasta, sem dependências de código dos outros repositórios.
