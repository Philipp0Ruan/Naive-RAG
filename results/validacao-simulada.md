# Validação simulada — 29/10/2026

- 15 testes locais passaram, incluindo falhas simuladas de autenticação, limite da API, conexão e respostas incompletas/vazias.
- As cinco perguntas foram executadas com corpus sintético, vetores programados e um cliente de LLM falso.
- O cenário sem evidência não tentou gerar uma resposta.
- A simulação bloqueou conexões de rede e a construção de um cliente OpenAI real.
- Os testes verificaram que o cenário não lê credenciais nem baixa o PDF.
- O notebook executou em kernel novo com MODO = "simulado".
- Python e notebook produziram as mesmas respostas fictícias e as mesmas fontes sintéticas.
- O índice do livro foi preservado, conferido por hash antes e depois do notebook.
- Os relatórios usam simulado: true e api_real_executada: false. Tokens e custo ficam como null.

Os textos são programados para testar a integração e não são respostas reais sobre Os Sertões. Os testes não medem qualidade semântica, latência ou custo de um LLM real. A geração real continua pendente da aprovação do usuário.
