"""Validação de integração com corpus, embeddings e cliente de LLM simulados.

Não lê credenciais, não baixa arquivos e não mede a qualidade de um LLM real.
"""

from __future__ import annotations

from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

from naive_rag import (RAIZ, Config, NaiveRAG, carregar_perguntas, dividir_trechos,
                       gerar_resposta, ler_json, salvar_json, salvar_markdown, sha256)

AVISO = ("SIMULAÇÃO: corpus sintético, vetores programados e resposta fictícia. "
         "Nenhuma API real foi chamada. Não avalia respostas sobre o livro.")
TEMAS = ("ambiente natural", "população sertaneja", "contexto do conflito",
         "Antônio Conselheiro", "crítica social e política")


class TokenizadorSimulado:
    def __call__(self, texto: str, **kwargs) -> dict:
        return {"offset_mapping": [(m.start(), m.end()) for m in re.finditer(r"\S+", texto)]}


class EmbeddingsSimulados:
    """Mapa explícito pergunta/documento → vetor. Não realiza busca semântica real."""

    tokenizer = TokenizadorSimulado()

    def __init__(self, perguntas: list[dict], trechos: list[dict]):
        self.mapa = {}
        self.dimensoes = len(perguntas) + 1
        base = np.eye(self.dimensoes, dtype=np.float32)
        for i, (pergunta, trecho) in enumerate(zip(perguntas, trechos)):
            self.mapa["query: " + pergunta["pergunta"]] = base[i]
            self.mapa["passage: " + trecho["text"]] = base[i]
        self.desconhecido = base[-1]

    def encode(self, textos, **kwargs) -> np.ndarray:
        return np.array([self.mapa.get(t, self.desconhecido) for t in textos], dtype=np.float32)


class ClienteSimulado:
    """Imita apenas o contrato da Responses API usado pelo projeto."""

    def __init__(self):
        self.responses = self
        self.chamadas = []

    def create(self, **argumentos):
        self.chamadas.append(argumentos)
        pagina = re.search(r"\[PDF p\. (\d+);", argumentos["input"])
        if pagina is None:
            raise AssertionError("A simulação esperava uma fonte no contexto.")
        texto = ("SIMULAÇÃO — resposta programada para testar o fluxo. "
                 "O documento de teste foi incluído no contexto "
                 f"[PDF p. {pagina.group(1)}]. Este texto é fictício e não responde "
                 "à questão histórica nem representa uma saída real da OpenAI.")
        return SimpleNamespace(status="completed", output_text=texto,
                               model="llm-simulado-v1", id=f"simulado-{len(self.chamadas)}",
                               usage=None)


def preparar_cenario(root: Path, perguntas: list[dict], base: Config) -> NaiveRAG:
    """Cria um índice sintético em uma pasta temporária, usando o formato real."""
    paginas = [{"pdf_page": i + 1, "printed_page": i + 1,
                "source": f"fixture://documento-sintetico/{i + 1}",
                "text": (f"DOCUMENTO SINTÉTICO {i + 1}. Tema de teste: {tema}. "
                         "Conteúdo fictício criado para validar a integração. "
                         "Não é uma passagem de Os Sertões.")}
               for i, tema in enumerate(TEMAS)]
    digest = hashlib.sha256(json.dumps(paginas, ensure_ascii=False).encode()).hexdigest()
    config = replace(base, pdf_url="fixture://corpus-sintetico", pdf_sha256=digest,
                     first_pdf_page=1, last_pdf_page=5, printed_page_offset=0,
                     embedding_model="embeddings-simulados", embedding_revision="fixture-v1",
                     top_k=2, min_similarity=0.5)
    trechos = dividir_trechos(paginas, TokenizadorSimulado(), config)
    modelo = EmbeddingsSimulados(perguntas, trechos)
    vetores = modelo.encode(["passage: " + t["text"] for t in trechos])
    storage = root / "storage"
    storage.mkdir(parents=True, exist_ok=True)
    np.save(storage / "embeddings.npy", vetores, allow_pickle=False)
    manifesto = {"simulado": True, "assinatura": config.assinatura(), "config": asdict(config),
                 "total_trechos": len(trechos), "dimensoes": vetores.shape[1],
                 "embeddings_sha256": sha256(storage / "embeddings.npy")}
    salvar_json(storage / "indice.json", {"manifesto": manifesto, "trechos": trechos})
    salvar_json(root / "evaluation" / "perguntas.json", {"perguntas": perguntas})
    rag = NaiveRAG(root, config)
    rag.__dict__["modelo"] = modelo
    rag.carregar_indice()
    return rag


def executar_simulacao(root: Path = RAIZ, nome: str = "simulacao") -> Path:
    """Exercita busca, contexto, geração simulada, citações e exportação sem rede."""
    if not re.fullmatch(r"[\w.-]+", nome) or nome in (".", ".."):
        raise ValueError("Use um nome de arquivo simples para a simulação.")
    root = Path(root)
    perguntas = carregar_perguntas(root)
    if len(perguntas) != len(TEMAS):
        raise ValueError("O cenário espera as cinco perguntas do desafio.")
    cliente = ClienteSimulado()

    def gerar_simulado(pergunta, contexto, config, pasta):
        return gerar_resposta(pergunta, contexto, config, pasta, client=cliente)

    bloqueio = AssertionError("A simulação não permite conexões de rede ou um cliente OpenAI real.")
    with TemporaryDirectory(prefix="naive-rag-simulado-") as temporario:
        rag = preparar_cenario(Path(temporario), perguntas, Config.carregar(root))
        # As mesmas funções de produção são usadas; só as dependências externas são substituídas.
        with patch("socket.socket.connect", side_effect=bloqueio), \
             patch("socket.socket.connect_ex", side_effect=bloqueio), \
             patch("socket.create_connection", side_effect=bloqueio), \
             patch("openai.OpenAI", side_effect=bloqueio), \
             patch("naive_rag.configuracao_openai", return_value={"model": "llm-simulado-v1", "temperature": None}), \
             patch("naive_rag.gerar_resposta", side_effect=gerar_simulado):
            caminho = rag.avaliar(nome="lote-simulado")
            negativo = rag.responder("Pergunta sem correspondência no corpus de teste.")
        dados = ler_json(caminho)
        if len(cliente.chamadas) != 5 or negativo["geracao_executada"]:
            raise AssertionError("Quantidade de chamadas simuladas ou cenário sem evidência inválido.")

    dados.update({"simulado": True, "aviso": AVISO, "api_real_executada": False,
                  "origem_dados": "corpus sintético e vetores programados",
                  "revisao_humana": "não avalia qualidade de LLM real",
                  "chamadas_simuladas": len(cliente.chamadas),
                  "cenario_sem_evidencia": negativo})
    for resultado in [*dados["resultados"], dados["cenario_sem_evidencia"]]:
        resultado.update({"modo": "simulado", "simulado": True,
                          "geracao_simulada": resultado["geracao_executada"],
                          "geracao_executada": False, "api_real_executada": False,
                          "uso_tokens": None, "custo": None})
        resultado["citacoes"]["revisao_semantica"] = "não avaliada: cenário sintético"
    destino = root / "results" / f"{nome}.json"
    salvar_json(destino, dados)
    salvar_markdown(destino.with_suffix(".md"), dados)
    return destino
