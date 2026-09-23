"""
Testes do processamento de registros (módulo `processador`) e da interface
de linha de comando (módulo `cli`), incluindo o tratamento de entradas vazias
e inválidas exigido pelo enunciado.
"""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from analisador import cli
from analisador.processador import (
    ErroDeEntrada,
    LinhaInvalida,
    Registro,
    analisar_arquivo,
    analisar_linha,
    analisar_texto,
    contagem_de_alertas,
    estatisticas_por_grandeza,
)

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"

LINHA_VALIDA = (
    "PA-BEL-004A|2026-09-21T14:35:02Z|-1.455833,-48.503889|"
    "TEMP=+27.4C;UMID=85%;PLUV=12.5mm|fw-v3.11.2-beta.4|!ALERTA:NIVEL2:CHUVA_FORTE"
)


class TesteLinhaValida(unittest.TestCase):
    def setUp(self):
        self.registro = analisar_linha(LINHA_VALIDA, numero=1)

    def teste_e_um_registro(self):
        self.assertIsInstance(self.registro, Registro)

    def teste_campos_extraidos(self):
        self.assertEqual(self.registro.codigo_estacao, "PA-BEL-004A")
        self.assertIsNone(self.registro.sub_estacao)
        self.assertEqual(self.registro.instante.year, 2026)
        self.assertAlmostEqual(self.registro.latitude, -1.455833)
        self.assertAlmostEqual(self.registro.longitude, -48.503889)
        self.assertEqual(len(self.registro.leituras), 3)
        self.assertEqual(self.registro.versao, (3, 11, 2))
        self.assertEqual(self.registro.pre_lancamento, "beta")
        self.assertFalse(self.registro.estavel)
        self.assertEqual(self.registro.alerta_nivel, 2)
        self.assertEqual(self.registro.alerta_codigo, "CHUVA_FORTE")

    def teste_alerta_opcional_pode_faltar(self):
        sem_alerta = LINHA_VALIDA.rsplit("|", 1)[0]
        registro = analisar_linha(sem_alerta)
        self.assertIsInstance(registro, Registro)
        self.assertIsNone(registro.alerta_nivel)

    def teste_sub_estacao(self):
        registro = analisar_linha(LINHA_VALIDA.replace("004A|", "004A.2|", 1))
        self.assertEqual(registro.sub_estacao, "2")


class TesteLinhasInvalidas(unittest.TestCase):
    def _mensagens(self, linha: str) -> str:
        resultado = analisar_linha(linha)
        self.assertIsInstance(resultado, LinhaInvalida)
        return " ".join(resultado.mensagens)

    def teste_linha_vazia(self):
        self.assertIn("vazia", self._mensagens("   "))

    def teste_linha_nula(self):
        self.assertIsInstance(analisar_linha(None), LinhaInvalida)

    def teste_numero_de_campos_errado(self):
        self.assertIn("campos", self._mensagens("PA-BEL-004A|2026-09-21T14:35:02Z"))

    def teste_codigo_invalido(self):
        self.assertIn("Campo 1", self._mensagens(LINHA_VALIDA.replace("PA-BEL", "pa-bel")))

    def teste_carimbo_invalido(self):
        self.assertIn("Campo 2", self._mensagens(LINHA_VALIDA.replace("T14:35:02Z", " 14:35:02")))

    def teste_data_inexistente_no_calendario(self):
        mensagem = self._mensagens(LINHA_VALIDA.replace("2026-09-21", "2026-02-30"))
        self.assertIn("calendário", mensagem)

    def teste_coordenada_invalida(self):
        self.assertIn("Campo 3", self._mensagens(
            LINHA_VALIDA.replace("-1.455833,-48.503889", "-1.45,-48.50")))

    def teste_coordenada_fora_da_faixa(self):
        mensagem = self._mensagens(
            LINHA_VALIDA.replace("-1.455833,-48.503889", "-91.000000,-48.503889"))
        self.assertIn("faixa geográfica", mensagem)

    def teste_leitura_invalida(self):
        self.assertIn("Campo 4", self._mensagens(LINHA_VALIDA.replace("TEMP=+27.4C", "TEMP=27.4")))

    def teste_firmware_invalido(self):
        self.assertIn("Campo 5", self._mensagens(
            LINHA_VALIDA.replace("fw-v3.11.2-beta.4", "fw-v3.11")))

    def teste_alerta_invalido(self):
        self.assertIn("Campo 6", self._mensagens(LINHA_VALIDA.replace("NIVEL2", "NIVEL4")))

    def teste_alerta_presente_e_vazio(self):
        self.assertIn("vazio", self._mensagens(LINHA_VALIDA.rsplit("|", 1)[0] + "|"))


class TesteAvisosSemanticos(unittest.TestCase):
    def teste_valor_fora_da_faixa_gera_aviso_sem_invalidar(self):
        registro = analisar_linha(LINHA_VALIDA.replace("TEMP=+27.4C", "TEMP=+99.9C"))
        self.assertIsInstance(registro, Registro)
        self.assertTrue(any("fora da faixa" in aviso for aviso in registro.avisos))
        self.assertTrue(registro.leituras[0].suspeita)

    def teste_codigo_de_alerta_fora_do_catalogo(self):
        registro = analisar_linha(LINHA_VALIDA.replace("CHUVA_FORTE", "NEVASCA_TROPICAL"))
        self.assertTrue(any("catálogo" in aviso for aviso in registro.avisos))

    def teste_unidade_incoerente_com_a_grandeza(self):
        registro = analisar_linha(LINHA_VALIDA.replace("UMID=85%", "UMID=85C"))
        self.assertTrue(any("deveria ser medida" in aviso for aviso in registro.avisos))


class TesteAnaliseDeTexto(unittest.TestCase):
    def teste_texto_vazio(self):
        with self.assertRaises(ErroDeEntrada):
            analisar_texto("")

    def teste_texto_nulo(self):
        with self.assertRaises(ErroDeEntrada):
            analisar_texto(None)

    def teste_apenas_comentarios(self):
        with self.assertRaises(ErroDeEntrada):
            analisar_texto("# apenas um comentário\n\n")

    def teste_comentarios_sao_ignorados(self):
        resultado = analisar_texto(f"# cabeçalho\n\n{LINHA_VALIDA}\n")
        self.assertEqual(len(resultado.registros), 1)
        self.assertEqual(resultado.linhas_ignoradas, 2)
        self.assertEqual(resultado.taxa_de_acerto, 100.0)

    def teste_mistura_de_validos_e_invalidos(self):
        texto = "\n".join([LINHA_VALIDA, "linha corrompida", LINHA_VALIDA])
        resultado = analisar_texto(texto)
        self.assertEqual(len(resultado.registros), 2)
        self.assertEqual(len(resultado.invalidas), 1)


class TesteAnaliseDeArquivo(unittest.TestCase):
    def teste_arquivo_de_exemplo(self):
        resultado = analisar_arquivo(DADOS / "telemetria_setembro.log")
        self.assertGreater(len(resultado.registros), 15)
        self.assertGreater(len(resultado.invalidas), 5)

    def teste_arquivo_inexistente(self):
        with self.assertRaises(ErroDeEntrada):
            analisar_arquivo(DADOS / "nao_existe.log")

    def teste_arquivo_vazio(self):
        with self.assertRaises(ErroDeEntrada):
            analisar_arquivo(DADOS / "vazio.log")

    def teste_arquivo_so_com_comentarios(self):
        with self.assertRaises(ErroDeEntrada):
            analisar_arquivo(DADOS / "somente_comentarios.log")

    def teste_caminho_vazio(self):
        with self.assertRaises(ErroDeEntrada):
            analisar_arquivo("")

    def teste_diretorio_no_lugar_de_arquivo(self):
        with self.assertRaises(ErroDeEntrada):
            analisar_arquivo(DADOS)


class TesteEstatisticas(unittest.TestCase):
    def setUp(self):
        self.resultado = analisar_arquivo(DADOS / "telemetria_setembro.log")

    def teste_estatisticas_por_grandeza(self):
        resumo = estatisticas_por_grandeza(self.resultado)
        self.assertIn("TEMP", resumo)
        self.assertLessEqual(resumo["TEMP"]["minimo"], resumo["TEMP"]["media"])
        self.assertLessEqual(resumo["TEMP"]["media"], resumo["TEMP"]["maximo"])
        self.assertEqual(resumo["UMID"]["unidade"], "%")

    def teste_contagem_de_alertas(self):
        contagem = contagem_de_alertas(self.resultado)
        self.assertTrue(set(contagem).issubset({1, 2, 3}))
        self.assertGreater(sum(contagem.values()), 0)


class TesteInterface(unittest.TestCase):
    def _executar(self, argumentos):
        saida = io.StringIO()
        with redirect_stdout(saida):
            codigo = cli.principal(argumentos)
        return codigo, saida.getvalue()

    def teste_analise_de_arquivo(self):
        codigo, saida = self._executar(["-a", str(DADOS / "telemetria_setembro.log")])
        self.assertEqual(codigo, 0)
        self.assertIn("RELATÓRIO DE ANÁLISE", saida)

    def teste_arquivo_inexistente_devolve_mensagem_clara(self):
        codigo, saida = self._executar(["-a", "caminho/que/nao/existe.log"])
        self.assertEqual(codigo, 2)
        self.assertIn("ERRO DE ENTRADA", saida)

    def teste_validacao_de_cadeia(self):
        codigo, saida = self._executar(["-e", "ER-03", "-c", "TEMP=+27.4C"])
        self.assertEqual(codigo, 0)
        self.assertIn("ACEITA", saida)
        self.assertIn("ok", saida)

    def teste_validacao_sem_indicar_a_er(self):
        codigo, saida = self._executar(["-c", "TEMP=+27.4C"])
        self.assertEqual(codigo, 2)
        self.assertIn("ERRO DE ENTRADA", saida)

    def teste_er_inexistente(self):
        codigo, saida = self._executar(["-e", "ER-42", "-c", "abc"])
        self.assertEqual(codigo, 2)
        self.assertIn("não existe", saida)

    def teste_linha_valida_pela_interface(self):
        codigo, saida = self._executar(["-l", LINHA_VALIDA])
        self.assertEqual(codigo, 0)
        self.assertIn("VÁLIDO", saida)

    def teste_linha_invalida_pela_interface(self):
        codigo, saida = self._executar(["-l", "isso não é um registro"])
        self.assertEqual(codigo, 1)
        self.assertIn("INVÁLIDO", saida)

    def teste_bateria_de_casos(self):
        codigo, saida = self._executar(["-t"])
        self.assertEqual(codigo, 0)
        self.assertIn("pleno acordo", saida)

    def teste_fichas(self):
        codigo, saida = self._executar(["-f"])
        self.assertEqual(codigo, 0)
        for identificador in ("ER-01", "ER-02", "ER-03", "ER-04", "ER-05", "ER-06"):
            self.assertIn(identificador, saida)


if __name__ == "__main__":
    unittest.main(verbosity=2)
