# Validação da implementação

Verificações feitas em 29/10/2026, com Python 3.12.10 no Windows.

- Nove testes locais passaram, sem chamadas à API real.
- `pip check` não encontrou dependências incompatíveis no ambiente instalado.
- O PDF foi conferido pelo SHA-256 registrado no `config.json`.
- O índice contém 1.176 trechos, 384 dimensões e 620 páginas com texto.
- O lote Python executou Q1 a Q5 no modo de recuperação, usando o modelo em cache sem acesso ao Hugging Face.
- O notebook executou todas as células em um kernel novo no mesmo modo.
- Python e notebook recuperaram os mesmos IDs de trechos nas cinco perguntas; as similaridades foram comparadas com tolerância de 0,000001.
- As fontes do contexto ficaram dentro das páginas 33 a 653, com numeração impressa correspondente e dentro do limite de contexto.
- A recarga do índice, o tratamento de credencial ausente e as regras do `.gitignore` foram conferidos.

O tempo da primeira consulta inclui carregar o modelo de embeddings. As demais consultas do mesmo processo reutilizam o modelo; isso deve ser considerado ao comparar latências.

Uma amostra dos resultados mostra trechos relacionados às perguntas, com evidências parciais, continuações de páginas e notas de rodapé. Isso não demonstra cobertura completa nem qualidade de uma resposta final.

A chave da OpenAI ainda não estava configurada nesta validação. Nenhuma resposta real de LLM foi gerada. O teste da API usa uma resposta simulada, e os relatórios de busca têm `resposta: null`.

Ainda falta executar a geração real, revisar as cinco respostas com a rubrica e testar a rejeição de uma pergunta sem evidência na obra com o LLM real.
