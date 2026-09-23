"""
Testes das Expressões Regulares (módulo `expressoes`).

Executáveis tanto com `python -m unittest` (biblioteca padrão) quanto com
`pytest`, que reconhece classes de unittest.
"""

from __future__ import annotations

import re
import unittest

from analisador.expressoes import (
    FICHAS,
    PADRAO_LEITURA_EXTRACAO,
    PADRAO_LEITURA_SENSOR,
    obter_ficha,
    validar,
)

RECURSOS_PROIBIDOS = [
    (r"\\[1-9]", "retroreferência"),
    (r"\(\?=", "lookahead positivo"),
    (r"\(\?!", "lookahead negativo"),
    (r"\(\?<", "lookbehind"),
    (r"\(\?R", "recursão"),
    (r"\(\?\(", "condicional"),
]


class TesteQuantidadeDeCasos(unittest.TestCase):
    """O trabalho exige no mínimo 6 cadeias aceitas e 6 rejeitadas por ER."""

    def teste_ha_seis_ou_mais_cadeias_de_cada_tipo(self):
        for ficha in FICHAS:
            with self.subTest(er=ficha.identificacao):
                self.assertGreaterEqual(len(ficha.aceitas), 6)
                self.assertGreaterEqual(len(ficha.rejeitadas), 6)

    def teste_ha_descricao_de_caso_limite(self):
        for ficha in FICHAS:
            with self.subTest(er=ficha.identificacao):
                self.assertTrue(ficha.caso_limite.strip())

    def teste_nao_ha_cadeia_repetida_entre_aceitas_e_rejeitadas(self):
        for ficha in FICHAS:
            with self.subTest(er=ficha.identificacao):
                self.assertFalse(set(ficha.aceitas) & set(ficha.rejeitadas))


class TesteCadeiasAceitas(unittest.TestCase):
    def teste_todas_as_cadeias_aceitas_casam_por_inteiro(self):
        for ficha in FICHAS:
            for cadeia in ficha.aceitas:
                with self.subTest(er=ficha.identificacao, cadeia=cadeia):
                    self.assertTrue(
                        ficha.aceita(cadeia),
                        f"{ficha.identificacao} deveria aceitar {cadeia!r}",
                    )


class TesteCadeiasRejeitadas(unittest.TestCase):
    def teste_todas_as_cadeias_rejeitadas_sao_recusadas(self):
        for ficha in FICHAS:
            for cadeia in ficha.rejeitadas:
                with self.subTest(er=ficha.identificacao, cadeia=cadeia):
                    self.assertFalse(
                        ficha.aceita(cadeia),
                        f"{ficha.identificacao} não deveria aceitar {cadeia!r}",
                    )


class TesteCasosLimite(unittest.TestCase):
    """Casos-limite citados explicitamente na ficha de cada ER."""

    def teste_er01_ponto_sem_digito(self):
        self.assertFalse(validar("ER-01", "PA-BEL-004A."))
        self.assertTrue(validar("ER-01", "PA-BEL-004A"))
        self.assertTrue(validar("ER-01", "PA-BEL-004A.1"))

    def teste_er02_fracao_vazia(self):
        self.assertFalse(validar("ER-02", "2026-09-21T14:35:02."))
        self.assertTrue(validar("ER-02", "2026-09-21T14:35:02"))

    def teste_er03_numero_sem_parte_inteira(self):
        self.assertFalse(validar("ER-03", "TEMP=.5C"))
        self.assertTrue(validar("ER-03", "TEMP=-0C"))

    def teste_er04_casas_decimais_insuficientes(self):
        self.assertFalse(validar("ER-04", "-1.45,-48.50"))
        self.assertTrue(validar("ER-04", "0.0000,0.0000"))

    def teste_er05_codigo_vazio(self):
        self.assertFalse(validar("ER-05", "!ALERTA:NIVEL2:"))
        self.assertTrue(validar("ER-05", "!ALERTA:NIVEL3:A"))

    def teste_er06_versao_incompleta(self):
        self.assertFalse(validar("ER-06", "fw-v3.11"))
        self.assertTrue(validar("ER-06", "fw-v0.0.1"))

    def teste_cadeia_vazia_nao_pertence_a_nenhuma_linguagem(self):
        for ficha in FICHAS:
            with self.subTest(er=ficha.identificacao):
                self.assertFalse(ficha.aceita(""))


class TesteAncoragemDaValidacao(unittest.TestCase):
    """`fullmatch` garante que prefixos e sufixos não sejam aceitos."""

    def teste_prefixo_valido_com_lixo_no_final(self):
        self.assertFalse(validar("ER-01", "PA-BEL-004A???"))
        self.assertFalse(validar("ER-03", "TEMP=+27.4C;UMID=85%"))
        self.assertFalse(validar("ER-06", "fw-v3.11.2 "))

    def teste_lixo_no_inicio(self):
        self.assertFalse(validar("ER-05", "X!ALERTA:NIVEL1:CHUVA"))
        self.assertFalse(validar("ER-02", " 2026-09-21T14:35:02"))


class TesteEntradasInvalidas(unittest.TestCase):
    def teste_valor_nulo_nao_quebra_o_validador(self):
        self.assertFalse(obter_ficha("ER-01").aceita(None))

    def teste_identificador_desconhecido(self):
        with self.assertRaises(KeyError):
            obter_ficha("ER-99")

    def teste_identificador_vazio(self):
        with self.assertRaises(KeyError):
            obter_ficha("   ")

    def teste_identificador_em_minusculas_funciona(self):
        self.assertEqual(obter_ficha("er-02").identificacao, "ER-02")


class TesteConformidadeComOGuia(unittest.TestCase):
    """Seção 4 do guia: recursos avançados não podem ser usados."""

    def teste_padroes_compilam(self):
        for ficha in FICHAS:
            with self.subTest(er=ficha.identificacao):
                self.assertIsInstance(re.compile(ficha.sintaxe), re.Pattern)

    def teste_sem_recursos_proibidos(self):
        for ficha in FICHAS:
            for padrao, nome in RECURSOS_PROIBIDOS:
                with self.subTest(er=ficha.identificacao, recurso=nome):
                    self.assertIsNone(
                        re.search(padrao, ficha.sintaxe),
                        f"{ficha.identificacao} usa {nome}, proibido pelo guia.",
                    )

    def teste_grupos_sao_nao_capturantes(self):
        for ficha in FICHAS:
            with self.subTest(er=ficha.identificacao):
                abertos = len(re.findall(r"(?<!\\)\(", ficha.sintaxe))
                nao_capturantes = len(re.findall(r"\(\?:", ficha.sintaxe))
                self.assertEqual(abertos, nao_capturantes)

    def teste_ficha_completa(self):
        for ficha in FICHAS:
            with self.subTest(er=ficha.identificacao):
                for campo in (
                    ficha.nome,
                    ficha.finalidade,
                    ficha.alfabeto,
                    ficha.linguagem,
                    ficha.er_formal,
                    ficha.sintaxe,
                    ficha.resultado_e_limite,
                ):
                    self.assertTrue(str(campo).strip())
                self.assertTrue(ficha.equivalencia)
                self.assertTrue(ficha.operadores)


class TestePadraoDeExtracao(unittest.TestCase):
    """O padrão auxiliar de extração reconhece a mesma linguagem da ER-03."""

    def teste_mesma_linguagem(self):
        ficha = obter_ficha("ER-03")
        extrator = re.compile(PADRAO_LEITURA_EXTRACAO)
        cadeias = ficha.aceitas + ficha.rejeitadas + ["ABC=1C", "AB=1C", "XYZ=1hPa"]
        for cadeia in cadeias:
            with self.subTest(cadeia=cadeia):
                self.assertEqual(
                    re.fullmatch(PADRAO_LEITURA_SENSOR, cadeia) is not None,
                    extrator.fullmatch(cadeia) is not None,
                )

    def teste_grupos_extraidos(self):
        casamento = re.fullmatch(PADRAO_LEITURA_EXTRACAO, "PRES=1012.75hPa")
        self.assertEqual(casamento.group("grandeza"), "PRES")
        self.assertEqual(casamento.group("valor"), "1012.75")
        self.assertEqual(casamento.group("unidade"), "hPa")


if __name__ == "__main__":
    unittest.main(verbosity=2)
