"""Cenários simulados de integração. Nenhum teste chama a API real."""

from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from openai import APIError

from naive_rag import (RAIZ, Config, NaiveRAG, gerar_resposta, ler_json, main,
                       salvar_json)
from simulacao import ClienteSimulado, executar_simulacao


class ErroOpenAISimulado(APIError):
    def __init__(self, status=None):
        super().__init__("erro simulado: detalhe que não deve aparecer no terminal",
                         request=SimpleNamespace(), body=None)
        self.status_code = status


class TestSimulacao(unittest.TestCase):
    def preparar(self, root):
        salvar_json(root/'config.json', ler_json(RAIZ/'config.json'))
        salvar_json(root/'evaluation/perguntas.json', ler_json(RAIZ/'evaluation/perguntas.json'))

    def test_cinco_perguntas_sem_chave_sem_pdf_e_sem_rede(self):
        with TemporaryDirectory() as pasta:
            root = Path(pasta)
            self.preparar(root)
            with patch('naive_rag.valor_ambiente', side_effect=AssertionError('Não ler credenciais')), \
                 patch('naive_rag.baixar_pdf', side_effect=AssertionError('Não baixar PDF')), \
                 redirect_stdout(io.StringIO()):
                arquivo = executar_simulacao(root)
            dados = ler_json(arquivo)
            self.assertTrue(dados['simulado'])
            self.assertFalse(dados['api_real_executada'])
            self.assertEqual(dados['chamadas_simuladas'], 5)
            self.assertEqual([r['id'] for r in dados['resultados']], ['Q1','Q2','Q3','Q4','Q5'])
            for i, item in enumerate(dados['resultados'], 1):
                self.assertEqual(item['modo'], 'simulado')
                self.assertTrue(item['geracao_simulada'])
                self.assertFalse(item['geracao_executada'])
                self.assertIn('SIMULAÇÃO', item['resposta'])
                self.assertEqual(item['citacoes']['paginas_citadas'], [i])
                self.assertEqual(item['citacoes']['paginas_fora_do_contexto'], [])
                self.assertIsNone(item['uso_tokens'])
                self.assertIsNone(item['custo'])
                self.assertTrue(item['fontes_contexto'][0]['source'].startswith('fixture://'))
            negativo = dados['cenario_sem_evidencia']
            self.assertFalse(negativo['geracao_simulada'])
            self.assertEqual(negativo['fontes_contexto'], [])
            self.assertIn('evidências suficientes', negativo['resposta'])
            self.assertFalse((root/'storage').exists())
            self.assertFalse((root/'.env').exists())
            markdown = arquivo.with_suffix('.md').read_text(encoding='utf-8')
            self.assertTrue(markdown.startswith('# SIMULAÇÃO'))
            self.assertIn('Nenhuma API real', markdown)

    def test_nome_nao_pode_sair_da_pasta_results(self):
        for nome in ('../fora', '..', '.', 'pasta/arquivo', 'pasta\\arquivo'):
            with self.subTest(nome=nome), self.assertRaises(ValueError):
                executar_simulacao(nome=nome)

    def test_resposta_incompleta_nao_e_aceita_como_sucesso(self):
        cliente = ClienteSimulado()
        cliente.create = lambda **kw: SimpleNamespace(status='incomplete', output_text='parcial')
        with patch('naive_rag.configuracao_openai', return_value={'model':'simulado','temperature':None}):
            with self.assertRaisesRegex(RuntimeError, 'resposta completa'):
                gerar_resposta('teste', '[PDF p. 1; trecho de teste]', Config.carregar(), client=cliente)

    def test_resposta_vazia_nao_e_aceita_como_sucesso(self):
        cliente = ClienteSimulado()
        cliente.create = lambda **kw: SimpleNamespace(status='completed', output_text='   ')
        with patch('naive_rag.configuracao_openai', return_value={'model':'simulado','temperature':None}):
            with self.assertRaisesRegex(RuntimeError, 'resposta completa'):
                gerar_resposta('teste', '[PDF p. 1; trecho de teste]', Config.carregar(), client=cliente)

    def test_credencial_invalida_e_limite_da_api_simulados(self):
        for status in (401, 429):
            saida = io.StringIO()
            with self.subTest(status=status), \
                 patch('sys.argv', ['naive_rag.py','responder','pergunta de teste']), \
                 patch('naive_rag.configuracao_openai', return_value={'model':'simulado','temperature':None}), \
                 patch.object(NaiveRAG,'responder',side_effect=ErroOpenAISimulado(status)), \
                 redirect_stderr(saida):
                self.assertEqual(main(), 1)
            self.assertIn(str(status), saida.getvalue())
            self.assertNotIn('detalhe que não deve', saida.getvalue())

    def test_falha_de_conexao_simulada(self):
        saida = io.StringIO()
        with patch('sys.argv', ['naive_rag.py','responder','pergunta de teste']), \
             patch('naive_rag.configuracao_openai', return_value={'model':'simulado','temperature':None}), \
             patch.object(NaiveRAG,'responder',side_effect=ErroOpenAISimulado()), \
             redirect_stderr(saida):
            self.assertEqual(main(), 1)
        self.assertIn('indisponível', saida.getvalue())


if __name__ == '__main__':
    unittest.main()
