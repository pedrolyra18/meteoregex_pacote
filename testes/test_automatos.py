"""
Testes dos AFNε (módulo `automatos`).

O teste central é o de **equivalência**: para toda cadeia de teste do projeto,
e para milhares de cadeias geradas aleatoriamente sobre o alfabeto de cada
autômato, a Expressão Regular e o AFNε devem produzir exatamente a mesma
resposta. É essa propriedade que sustenta a exigência do enunciado de que
ER formal, padrão do código, testes e AFNε representem a mesma linguagem.
"""

from __future__ import annotations

import random
import unittest

from analisador.automatos import AUTOMATOS, CLASSES, EPSILON, obter_automato
from analisador.expressoes import FICHAS, FICHAS_POR_ID

TODAS_AS_CADEIAS = [c for f in FICHAS for c in f.aceitas + f.rejeitadas]
SEMENTE = 20261002


class TesteEstruturaDosAutomatos(unittest.TestCase):
    def teste_existe_um_automato_por_expressao(self):
        self.assertEqual(set(AUTOMATOS), set(FICHAS_POR_ID))

    def teste_estado_inicial_e_finais_pertencem_a_Q(self):
        for identificador, automato in AUTOMATOS.items():
            with self.subTest(er=identificador):
                self.assertIn(automato.inicial, automato.estados)
                self.assertTrue(automato.finais)
                for final in automato.finais:
                    self.assertIn(final, automato.estados)

    def teste_transicoes_referenciam_estados_existentes(self):
        for identificador, automato in AUTOMATOS.items():
            for origem, rotulo, destino in automato.transicoes:
                with self.subTest(er=identificador, t=(origem, rotulo, destino)):
                    self.assertIn(origem, automato.estados)
                    self.assertIn(destino, automato.estados)
                    self.assertTrue(rotulo == EPSILON or rotulo in CLASSES
                                    or len(rotulo) == 1)

    def teste_todo_automato_possui_movimentos_vazios(self):
        for identificador, automato in AUTOMATOS.items():
            with self.subTest(er=identificador):
                self.assertGreater(
                    len(automato.movimentos_vazios), 0,
                    f"{identificador} precisa ter ao menos um movimento ε.",
                )

    def teste_estados_alcancaveis_a_partir_do_inicial(self):
        for identificador, automato in AUTOMATOS.items():
            alcancados = {automato.inicial}
            mudou = True
            while mudou:
                mudou = False
                for origem, _, destino in automato.transicoes:
                    if origem in alcancados and destino not in alcancados:
                        alcancados.add(destino)
                        mudou = True
            with self.subTest(er=identificador):
                self.assertEqual(set(automato.estados), alcancados)

    def teste_descricao_formal_menciona_os_componentes(self):
        texto = obter_automato("ER-01").formal()
        for marcador in ("Q  =", "Σ  =", "q0 =", "F  =", "δ:"):
            self.assertIn(marcador, texto)


class TesteAceitacaoPeloAutomato(unittest.TestCase):
    def teste_cadeias_aceitas(self):
        for ficha in FICHAS:
            automato = obter_automato(ficha.identificacao)
            for cadeia in ficha.aceitas:
                with self.subTest(er=ficha.identificacao, cadeia=cadeia):
                    self.assertTrue(automato.aceita(cadeia))

    def teste_cadeias_rejeitadas(self):
        for ficha in FICHAS:
            automato = obter_automato(ficha.identificacao)
            for cadeia in ficha.rejeitadas:
                with self.subTest(er=ficha.identificacao, cadeia=cadeia):
                    self.assertFalse(automato.aceita(cadeia))

    def teste_palavra_vazia_e_rejeitada(self):
        for identificador, automato in AUTOMATOS.items():
            with self.subTest(er=identificador):
                self.assertFalse(automato.aceita(""))

    def teste_trilha_registra_cada_simbolo(self):
        automato = obter_automato("ER-05")
        trilha = automato.trilha("!ALERTA:NIVEL3:A")
        self.assertEqual(len(trilha), len("!ALERTA:NIVEL3:A") + 1)
        self.assertTrue(trilha[-1][1] & automato.finais)


class TesteEquivalenciaEntreERealAFNe(unittest.TestCase):
    """ER e AFNε devem concordar em todas as cadeias testadas."""

    def teste_concordancia_em_todas_as_cadeias_do_projeto(self):
        for ficha in FICHAS:
            automato = obter_automato(ficha.identificacao)
            for cadeia in TODAS_AS_CADEIAS:
                with self.subTest(er=ficha.identificacao, cadeia=cadeia):
                    self.assertEqual(ficha.aceita(cadeia), automato.aceita(cadeia))

    def teste_concordancia_em_cadeias_aleatorias(self):
        sorteio = random.Random(SEMENTE)
        for ficha in FICHAS:
            automato = obter_automato(ficha.identificacao)
            alfabeto = sorted(automato.alfabeto)
            divergencias = []
            for _ in range(2000):
                tamanho = sorteio.randint(0, 24)
                cadeia = "".join(sorteio.choice(alfabeto) for _ in range(tamanho))
                if ficha.aceita(cadeia) != automato.aceita(cadeia):
                    divergencias.append(cadeia)
            with self.subTest(er=ficha.identificacao, origem="aleatória"):
                self.assertEqual(divergencias, [])

    def teste_concordancia_em_mutacoes_das_cadeias_aceitas(self):
        """Mutações de cadeias válidas exploram as fronteiras da linguagem."""
        sorteio = random.Random(SEMENTE + 1)
        for ficha in FICHAS:
            automato = obter_automato(ficha.identificacao)
            alfabeto = sorted(automato.alfabeto)
            divergencias = []
            for base in ficha.aceitas:
                for _ in range(200):
                    lista = list(base)
                    operacao = sorteio.choice(("troca", "remove", "insere"))
                    posicao = sorteio.randrange(len(lista))
                    if operacao == "troca":
                        lista[posicao] = sorteio.choice(alfabeto)
                    elif operacao == "remove":
                        del lista[posicao]
                    else:
                        lista.insert(posicao, sorteio.choice(alfabeto))
                    mutante = "".join(lista)
                    if ficha.aceita(mutante) != automato.aceita(mutante):
                        divergencias.append(mutante)
            with self.subTest(er=ficha.identificacao, origem="mutação"):
                self.assertEqual(divergencias, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
