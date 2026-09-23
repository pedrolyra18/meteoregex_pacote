"""
Módulo `automatos`
==================

Construção e simulação dos **AFNε** (autômatos finitos não determinísticos com
movimentos vazios) correspondentes às Expressões Regulares do módulo
`expressoes`.

Cada autômato é montado com um pequeno construtor que reproduz, passo a passo,
as regras da construção de Thompson vistas na disciplina:

    concatenação  r s      -> estados em série
    união         r | s    -> ε a partir de um estado de escolha e ε para um
                              estado de junção
    fecho +       r+       -> aresta ε de retorno ao estado anterior
    fecho *       r*       -> aresta ε de retorno + aresta ε de desvio
    opcional      r?       -> aresta ε de desvio (ramo da palavra vazia)
    {m,n}         r{m,n}   -> m cópias em série e (n-m) cópias com saída por ε

Assim, a cadeia de estados desenhada nos diagramas é literalmente a mesma que o
programa simula — o que permite ao conjunto de testes verificar que
**ER e AFNε reconhecem a mesma linguagem**.

Para manter os diagramas legíveis, as transições podem ser rotuladas por
*classes* de símbolos (M, D, S, N). Uma transição rotulada por uma classe é uma
abreviação da união das transições sobre cada símbolo da classe, exatamente
como `[A-Z]` abrevia `(A | B | ... | Z)`.
"""

from __future__ import annotations

import string
from dataclasses import dataclass, field

EPSILON = "ε"

# Rótulos de classe. São escritos entre colchetes angulares para que jamais
# sejam confundidos com um símbolo literal do alfabeto (a letra 'N' de "NIVEL",
# por exemplo, é literal; ⟨N⟩ é a classe dos dígitos 1 a 3).
CL_M = "⟨M⟩"
CL_D = "⟨D⟩"
CL_S = "⟨S⟩"
CL_N = "⟨N⟩"

#: Classes de símbolos usadas nos rótulos das transições.
CLASSES: dict[str, set[str]] = {
    CL_M: set(string.ascii_uppercase),          # [A-Z]
    CL_D: set(string.digits),                   # [0-9]
    CL_S: {"+", "-"},                           # [+-]
    CL_N: {"1", "2", "3"},                      # [1-3]
}

DESCRICAO_CLASSES: dict[str, str] = {
    CL_M: "⟨M⟩ = {A, B, ..., Z}  (abrevia [A-Z])",
    CL_D: "⟨D⟩ = {0, 1, ..., 9}  (abrevia [0-9])",
    CL_S: "⟨S⟩ = {+, -}          (abrevia [+-])",
    CL_N: "⟨N⟩ = {1, 2, 3}       (abrevia [1-3])",
}


# ---------------------------------------------------------------------------
# Estrutura do autômato
# ---------------------------------------------------------------------------


@dataclass
class AFNe:
    """AFNε = (Q, Σ, δ, q0, F)."""

    identificacao: str
    nome: str
    estados: list[str] = field(default_factory=list)
    transicoes: list[tuple[str, str, str]] = field(default_factory=list)
    inicial: str = "q0"
    finais: set[str] = field(default_factory=set)

    # -- consultas -----------------------------------------------------------
    @property
    def rotulos(self) -> list[str]:
        vistos: list[str] = []
        for _, r, _ in self.transicoes:
            if r not in vistos:
                vistos.append(r)
        return vistos

    @property
    def alfabeto(self) -> set[str]:
        """Σ: símbolos consumíveis (classes já expandidas, sem ε)."""
        simbolos: set[str] = set()
        for _, rotulo, _ in self.transicoes:
            if rotulo == EPSILON:
                continue
            simbolos |= CLASSES.get(rotulo, {rotulo})
        return simbolos

    @property
    def movimentos_vazios(self) -> list[tuple[str, str, str]]:
        return [t for t in self.transicoes if t[1] == EPSILON]

    # -- simulação -----------------------------------------------------------
    def _casa(self, rotulo: str, simbolo: str) -> bool:
        if rotulo == EPSILON:
            return False
        if rotulo in CLASSES:
            return simbolo in CLASSES[rotulo]
        return rotulo == simbolo

    def fecho_epsilon(self, conjunto: set[str]) -> set[str]:
        """ε-fecho: todos os estados alcançáveis apenas por movimentos vazios."""
        pilha = list(conjunto)
        alcancados = set(conjunto)
        while pilha:
            atual = pilha.pop()
            for origem, rotulo, destino in self.transicoes:
                if origem == atual and rotulo == EPSILON and destino not in alcancados:
                    alcancados.add(destino)
                    pilha.append(destino)
        return alcancados

    def mover(self, conjunto: set[str], simbolo: str) -> set[str]:
        destinos = {
            destino
            for origem, rotulo, destino in self.transicoes
            if origem in conjunto and self._casa(rotulo, simbolo)
        }
        return self.fecho_epsilon(destinos)

    def aceita(self, cadeia: str) -> bool:
        """Simula o AFNε sobre a cadeia inteira (aceitação em estado final)."""
        if cadeia is None:
            return False
        atuais = self.fecho_epsilon({self.inicial})
        for simbolo in cadeia:
            atuais = self.mover(atuais, simbolo)
            if not atuais:
                return False
        return bool(atuais & self.finais)

    def trilha(self, cadeia: str) -> list[tuple[str, set[str]]]:
        """Histórico de conjuntos de estados, útil para a demonstração."""
        atuais = self.fecho_epsilon({self.inicial})
        historico = [("(início, ε-fecho)", set(atuais))]
        for simbolo in cadeia or "":
            atuais = self.mover(atuais, simbolo)
            historico.append((simbolo, set(atuais)))
            if not atuais:
                break
        return historico

    # -- descrição formal ----------------------------------------------------
    def formal(self) -> str:
        linhas = [
            f"AFNε {self.identificacao} — {self.nome}",
            f"Q  = {{{', '.join(self.estados)}}}   (|Q| = {len(self.estados)})",
            "Σ  = " + ", ".join(
                DESCRICAO_CLASSES[r] if r in CLASSES else f"'{r}'"
                for r in self.rotulos
                if r != EPSILON
            ),
            f"q0 = {self.inicial}",
            f"F  = {{{', '.join(sorted(self.finais, key=_ordem))}}}",
            f"Movimentos vazios: {len(self.movimentos_vazios)}",
            "δ:",
        ]
        for origem, rotulo, destino in self.transicoes:
            linhas.append(f"    δ({origem}, {rotulo}) ∋ {destino}")
        return "\n".join(linhas)


def _ordem(estado: str) -> int:
    return int(estado[1:])


# ---------------------------------------------------------------------------
# Construtor
# ---------------------------------------------------------------------------


class ConstrutorAFNe:
    """Monta um AFNε aplicando as construções elementares de Thompson."""

    def __init__(self, identificacao: str, nome: str) -> None:
        self.afne = AFNe(identificacao=identificacao, nome=nome)
        self._contador = 0
        self.inicial = self.novo()
        self.afne.inicial = self.inicial

    # -- primitivas ----------------------------------------------------------
    def novo(self) -> str:
        estado = f"q{self._contador}"
        self._contador += 1
        self.afne.estados.append(estado)
        return estado

    def liga(self, origem: str, rotulo: str, destino: str) -> None:
        self.afne.transicoes.append((origem, rotulo, destino))

    def eps(self, origem: str, destino: str) -> None:
        self.liga(origem, EPSILON, destino)

    # -- construções ---------------------------------------------------------
    def simbolo(self, origem: str, rotulo: str) -> str:
        destino = self.novo()
        self.liga(origem, rotulo, destino)
        return destino

    def sequencia(self, origem: str, rotulos) -> str:
        atual = origem
        for rotulo in rotulos:
            atual = self.simbolo(atual, rotulo)
        return atual

    def mais(self, origem: str, rotulo: str) -> str:
        """r+ : uma ocorrência obrigatória e retorno por ε."""
        destino = self.simbolo(origem, rotulo)
        self.eps(destino, origem)
        return destino

    def estrela(self, origem: str, rotulo: str) -> str:
        """r* : como r+, acrescido do desvio ε (ramo da palavra vazia)."""
        destino = self.simbolo(origem, rotulo)
        self.eps(destino, origem)
        saida = self.novo()
        self.eps(origem, saida)
        return saida

    def uniao(self, origem: str, alternativas) -> str:
        """união de cadeias de rótulos: ε para cada ramo e ε para a junção."""
        juncao = self.novo()
        for alternativa in alternativas:
            entrada = self.novo()
            self.eps(origem, entrada)
            fim = self.sequencia(entrada, alternativa)
            self.eps(fim, juncao)
        return juncao

    def opcional(self, origem: str, construcao) -> str:
        """r? : ramo ε de desvio + ramo construído por `construcao`."""
        juncao = self.novo()
        self.eps(origem, juncao)          # ramo ε (ausência do bloco)
        entrada = self.novo()
        self.eps(origem, entrada)
        fim = construcao(self, entrada)
        self.eps(fim, juncao)
        return juncao

    def estrela_bloco(self, origem: str, construcao) -> str:
        """(r)* para um bloco composto: retorno por ε e desvio por ε."""
        entrada = self.novo()
        self.eps(origem, entrada)
        fim = construcao(self, entrada)
        self.eps(fim, origem)             # retorno: repete o bloco
        saida = self.novo()
        self.eps(origem, saida)           # desvio: zero ocorrências
        return saida

    def repeticao(self, origem: str, rotulo: str, minimo: int, maximo: int) -> str:
        """r{m,n} : m cópias obrigatórias e (n-m) cópias com saída por ε."""
        atual = origem
        for _ in range(minimo):
            atual = self.simbolo(atual, rotulo)
        saida = self.novo()
        self.eps(atual, saida)
        for _ in range(maximo - minimo):
            atual = self.simbolo(atual, rotulo)
            self.eps(atual, saida)
        return saida

    def exata(self, origem: str, rotulo: str, quantidade: int) -> str:
        """r{m} : concatenação de m cópias."""
        return self.sequencia(origem, [rotulo] * quantidade)

    # -- fechamento ----------------------------------------------------------
    def finalizar(self, *finais: str) -> AFNe:
        self.afne.finais = set(finais)
        return self.afne


# ---------------------------------------------------------------------------
# Os seis autômatos
# ---------------------------------------------------------------------------


def _afne_er01() -> AFNe:
    """[A-Z]{2}-[A-Z]{3}-[0-9]{3}[A-Z](?:\\.[0-9]{1,2})?"""
    c = ConstrutorAFNe("ER-01", "Código de estação meteorológica")
    s = c.sequencia(c.inicial, [CL_M, CL_M, "-", CL_M, CL_M, CL_M, "-", CL_D, CL_D, CL_D, CL_M])

    def sufixo(cc: ConstrutorAFNe, entrada: str) -> str:
        meio = cc.sequencia(entrada, [".", CL_D])
        return cc.repeticao(meio, CL_D, 0, 1)

    fim = c.opcional(s, sufixo)
    return c.finalizar(fim)


def _afne_er02() -> AFNe:
    """[0-9]{4}-...T...(?:\\.[0-9]{1,3})?(?:Z|[+-][0-9]{2}:[0-9]{2})?"""
    c = ConstrutorAFNe("ER-02", "Carimbo temporal ISO-8601")
    s = c.exata(c.inicial, CL_D, 4)
    s = c.simbolo(s, "-")
    s = c.exata(s, CL_D, 2)
    s = c.simbolo(s, "-")
    s = c.exata(s, CL_D, 2)
    s = c.simbolo(s, "T")
    s = c.exata(s, CL_D, 2)
    s = c.simbolo(s, ":")
    s = c.exata(s, CL_D, 2)
    s = c.simbolo(s, ":")
    s = c.exata(s, CL_D, 2)

    def fracao(cc: ConstrutorAFNe, entrada: str) -> str:
        ponto = cc.simbolo(entrada, ".")
        return cc.repeticao(ponto, CL_D, 1, 3)

    s = c.opcional(s, fracao)

    def fuso(cc: ConstrutorAFNe, entrada: str) -> str:
        juncao = cc.novo()
        # ramo 1: Z
        z = cc.simbolo(entrada, "Z")
        cc.eps(z, juncao)
        # ramo 2: [+-] D D : D D
        desl = cc.simbolo(entrada, CL_S)
        desl = cc.exata(desl, CL_D, 2)
        desl = cc.simbolo(desl, ":")
        desl = cc.exata(desl, CL_D, 2)
        cc.eps(desl, juncao)
        return juncao

    fim = c.opcional(s, fuso)
    return c.finalizar(fim)


def _afne_er03() -> AFNe:
    """[A-Z]{3,4}=[+-]?[0-9]+(?:\\.[0-9]+)?(?:C|%|mm|hPa|m/s)"""
    c = ConstrutorAFNe("ER-03", "Leitura de sensor com unidade")
    s = c.repeticao(c.inicial, CL_M, 3, 4)
    s = c.simbolo(s, "=")
    s = c.repeticao(s, CL_S, 0, 1)          # sinal opcional
    s = c.mais(s, CL_D)                     # parte inteira

    def fracionaria(cc: ConstrutorAFNe, entrada: str) -> str:
        ponto = cc.simbolo(entrada, ".")
        return cc.mais(ponto, CL_D)

    s = c.opcional(s, fracionaria)
    fim = c.uniao(
        s,
        [["C"], ["%"], ["m", "m"], ["h", "P", "a"], ["m", "/", "s"]],
    )
    return c.finalizar(fim)


def _afne_er04() -> AFNe:
    """[+-]?[0-9]{1,3}\\.[0-9]{4,6},[+-]?[0-9]{1,3}\\.[0-9]{4,6}"""
    c = ConstrutorAFNe("ER-04", "Par de coordenadas geodésicas decimais")

    def numero(construtor: ConstrutorAFNe, entrada: str) -> str:
        atual = construtor.repeticao(entrada, CL_S, 0, 1)
        atual = construtor.repeticao(atual, CL_D, 1, 3)
        atual = construtor.simbolo(atual, ".")
        return construtor.repeticao(atual, CL_D, 4, 6)

    s = numero(c, c.inicial)
    s = c.simbolo(s, ",")
    fim = numero(c, s)
    return c.finalizar(fim)


def _afne_er05() -> AFNe:
    """!ALERTA:NIVEL[1-3]:[A-Z]+(?:_[A-Z]+)*"""
    c = ConstrutorAFNe("ER-05", "Alerta hidrometeorológico")
    s = c.sequencia(c.inicial, list("!ALERTA:NIVEL"))
    s = c.simbolo(s, CL_N)
    s = c.simbolo(s, ":")
    s = c.mais(s, CL_M)

    def palavra_extra(cc: ConstrutorAFNe, entrada: str) -> str:
        traco = cc.simbolo(entrada, "_")
        return cc.mais(traco, CL_M)

    fim = c.estrela_bloco(s, palavra_extra)
    return c.finalizar(fim)


def _afne_er06() -> AFNe:
    """fw-v[0-9]+(?:\\.[0-9]+){2}(?:-(?:alpha|beta|rc)\\.[0-9]+)?"""
    c = ConstrutorAFNe("ER-06", "Versão de firmware da estação")
    s = c.sequencia(c.inicial, list("fw-v"))
    s = c.mais(s, CL_D)
    for _ in range(2):                      # {2}
        s = c.simbolo(s, ".")
        s = c.mais(s, CL_D)

    def rotulo(cc: ConstrutorAFNe, entrada: str) -> str:
        traco = cc.simbolo(entrada, "-")
        tipo = cc.uniao(traco, [list("alpha"), list("beta"), list("rc")])
        ponto = cc.simbolo(tipo, ".")
        return cc.mais(ponto, CL_D)

    fim = c.opcional(s, rotulo)
    return c.finalizar(fim)


AUTOMATOS: dict[str, AFNe] = {
    "ER-01": _afne_er01(),
    "ER-02": _afne_er02(),
    "ER-03": _afne_er03(),
    "ER-04": _afne_er04(),
    "ER-05": _afne_er05(),
    "ER-06": _afne_er06(),
}


def obter_automato(identificador: str) -> AFNe:
    chave = (identificador or "").strip().upper()
    if chave not in AUTOMATOS:
        raise KeyError(
            f"Não há AFNε para '{identificador}'. "
            f"Disponíveis: {', '.join(AUTOMATOS)}."
        )
    return AUTOMATOS[chave]
