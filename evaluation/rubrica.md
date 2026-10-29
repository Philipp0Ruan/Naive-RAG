# Revisão das respostas

Avaliar cada pergunta depois de executar o modo de geração com a API real. Um relatório de busca contém somente trechos e não recebe nota de qualidade de resposta.

| Critério | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Aderência à pergunta | Não responde | Responde parcialmente | Responde aos pontos pedidos |
| Sustentação nas fontes | Afirmações centrais sem evidência | Parte das afirmações é sustentada | Afirmações centrais sustentadas pelos trechos |
| Referências | Páginas inválidas ou ausentes | Referências incompletas | Páginas válidas e relacionadas às afirmações |
| Limitações | Inventa ou omite lacunas relevantes | Reconhece parte das lacunas | Explicita quando a evidência é insuficiente |
| Contexto histórico | Trata concepções de época como fatos atuais | Faz distinção parcial | Distingue claramente a visão do autor |

Para cada Q1 a Q5, registrar as notas, o trecho que justifica a avaliação, páginas conferidas no PDF e observações. O total pode ajudar a comparar execuções, mas não é uma medida automática de verdade.

Revisar especialmente:

- Q1: ambiente natural e influência sobre a vida dos habitantes.
- Q2: características dos sertanejos e relação com o ambiente.
- Q3: contexto histórico e político do conflito.
- Q4: representação de Antônio Conselheiro e seu papel.
- Q5: crítica social e política e visão do Brasil da época.

Também testar uma pergunta sem evidência no livro. O modelo deve declarar que o contexto não sustenta a resposta. Uma busca vetorial sempre pode devolver vizinhos; o simples retorno de trechos não prova relevância.

Os campos de conferência de citação no JSON validam apenas a presença do número da página no contexto. A sustentação semântica continua pendente até esta revisão.
