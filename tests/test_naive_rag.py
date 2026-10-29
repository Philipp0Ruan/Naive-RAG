"""Testes locais: sem baixar modelos e sem chamadas pagas à OpenAI."""

from dataclasses import replace
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

from naive_rag import (Config, NaiveRAG, conferir_citacoes, configuracao_openai,
                       dividir_trechos, gerar_resposta, limpar_texto,
                       montar_contexto, salvar_json, sha256)


def config(**kwargs):
    valores = dict(pdf_url="https://example.com/livro.pdf", pdf_sha256="abc",
                   first_pdf_page=33, last_pdf_page=653, printed_page_offset=30,
                   embedding_model="teste", embedding_revision="versao")
    return Config(**(valores | kwargs))


def trecho(numero=33, texto="O sertanejo resiste à seca."):
    return {"id": f"p{numero}", "pdf_page": numero, "printed_page": numero - 30,
            "source": "livro.pdf", "text": texto}


class Tokenizador:
    def __call__(self, texto, **kwargs):
        return {"offset_mapping": [(m.start(), m.end()) for m in re.finditer(r"\S+", texto)]}


class Modelo:
    def encode(self, textos, **kwargs):
        return np.array([[1., 0.] for _ in textos], dtype=np.float32)


class TestNaiveRAG(unittest.TestCase):
    def test_limpeza_preserva_acentos_e_remove_margens(self):
        bruto = ("os sertões | euclides da cunha 3\nO ser-\ntanejo é forte.\n"
                 "sub-\n-raças\n1 • Os sertoes - BBB - 3ª PROVA.indd 3 09/05/14 00:33")
        self.assertEqual(limpar_texto(bruto), "O sertanejo é forte. sub-raças")

    def test_janelas_sem_lacunas_e_com_sobreposicao(self):
        cfg = config(chunk_tokens=4, overlap_tokens=1)
        texto = "zero um dois três quatro cinco seis sete oito"
        partes = dividir_trechos([trecho(texto=texto)], Tokenizador(), cfg)
        self.assertEqual([(p['token_start'], p['token_end']) for p in partes], [(0,4),(3,7),(6,9)])
        self.assertEqual(partes[1]['text'], "três quatro cinco seis")
        self.assertTrue(all(p['pdf_page'] == 33 for p in partes))

    def test_hifenizacao_real_desta_edicao(self):
        bruto = 'biblioteca básica brasileira – cultive um livro\n150\nA estratifi -\ncação. sub -\n-raças.\n´'
        self.assertEqual(limpar_texto(bruto), 'A estratificação. sub-raças.')

    def test_contexto_limita_trechos_sem_cortar_texto(self):
        fontes = [trecho(), trecho(34)]
        primeiro, _ = montar_contexto(fontes[:1], 1000)
        contexto, usadas = montar_contexto(fontes, len(primeiro))
        self.assertEqual(contexto, primeiro)
        self.assertEqual(usadas, fontes[:1])
        self.assertEqual(montar_contexto(fontes, 2), ("", []))

    def test_citacao_fora_das_fontes_e_detectada(self):
        checagem = conferir_citacoes("Afirmação [PDF p. 33]. Outra [PDF p. 999].", [trecho()])
        self.assertEqual(checagem['paginas_fora_do_contexto'], [999])
        self.assertEqual(checagem['revisao_semantica'], 'pendente')

    def test_busca_cosseno_persistencia_e_indice_alterado(self):
        with TemporaryDirectory() as diretorio:
            root = Path(diretorio)
            storage = root / 'storage'
            storage.mkdir()
            cfg = config()
            vetores = np.array([[0.,1.],[1.,0.]], dtype=np.float32)
            np.save(storage/'embeddings.npy', vetores)
            manifesto = {'assinatura':cfg.assinatura(), 'dimensoes':2,
                         'embeddings_sha256':sha256(storage/'embeddings.npy')}
            salvar_json(storage/'indice.json', {'manifesto':manifesto,'trechos':[trecho(33),trecho(34)]})
            rag = NaiveRAG(root, cfg)
            rag.__dict__['modelo'] = Modelo()
            self.assertEqual(rag.buscar('sertão', 1)[0]['pdf_page'], 34)
            with self.assertRaises(ValueError):
                rag.buscar('')
            with self.assertRaises(ValueError):
                NaiveRAG(root, replace(cfg, chunk_tokens=300)).carregar_indice()
            (storage/'embeddings.npy').write_bytes(b'corrompido')
            with self.assertRaisesRegex(ValueError, 'alterados'):
                NaiveRAG(root, cfg).carregar_indice()

    def test_filtro_sem_evidencia_nao_chama_llm(self):
        rag = NaiveRAG(config=config())
        with patch.object(rag, 'buscar', return_value=[]), patch('naive_rag.gerar_resposta') as gerar:
            resposta = rag.responder('Quem venceu a Copa de 2022?')
        gerar.assert_not_called()
        self.assertFalse(resposta['geracao_executada'])
        self.assertIn('evidências suficientes', resposta['resposta'])

    def test_chave_ausente_e_env_recarregado(self):
        with TemporaryDirectory() as diretorio, patch.dict('os.environ', {}, clear=True):
            root = Path(diretorio)
            with self.assertRaisesRegex(ValueError, 'OPENAI_API_KEY'):
                configuracao_openai(root)
            (root/'.env').write_text('OPENAI_API_KEY=chave-ficticia\nOPENAI_MODEL=teste\n', encoding='utf-8')
            self.assertEqual(configuracao_openai(root)['model'], 'teste')

    def test_api_montagem_e_resposta_simulada(self):
        class Respostas:
            def create(self, **kwargs):
                self.argumentos = kwargs
                return SimpleNamespace(status='completed', output_text='Resposta [PDF p. 33].',
                                       model='modelo-teste', id='id-teste', usage=None)
        respostas = Respostas()
        with patch('naive_rag.configuracao_openai', return_value={'model':'teste','temperature':None}):
            resultado = gerar_resposta('pergunta', 'contexto', config(),
                                       client=SimpleNamespace(responses=respostas))
        self.assertFalse(respostas.argumentos['store'])
        self.assertNotIn('temperature', respostas.argumentos)
        self.assertIsNone(resultado['custo'])
        self.assertIn('[PDF p. 33]', resultado['resposta'])


if __name__ == '__main__':
    unittest.main()
