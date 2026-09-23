"""
Módulo `processador`
====================

Núcleo da aplicação **MeteoRegex**: transforma linhas de telemetria bruta em
registros estruturados, aplicando as seis Expressões Regulares do módulo
`expressoes` e, em seguida, as verificações semânticas que uma linguagem
regular não é capaz de expressar (faixas numéricas, calendário, catálogo).

Formato de um registro (campos separados por '|'):

    codigo | carimbo | coordenadas | leituras | firmware [ | alerta ]
      ER-01   ER-02      ER-04        ER-03      ER-06        ER-05

O sexto campo é opcional. Linhas em branco e linhas iniciadas por '#' são
tratadas como comentários e ignoradas.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .expressoes import (
    ER01,
    ER02,
    ER03,
    ER04,
    ER05,
    ER06,
    PADRAO_LEITURA_EXTRACAO,
)

SEPARADOR_CAMPOS = "|"
SEPARADOR_LEITURAS = ";"
MARCA_COMENTARIO = "#"

_EXTRATOR_LEITURA = re.compile(PADRAO_LEITURA_EXTRACAO)

#: Faixas de plausibilidade física por grandeza (mínimo, máximo, unidade).
FAIXAS_PLAUSIVEIS: dict[str, tuple[float, float, str]] = {
    "TEMP": (-15.0, 55.0, "C"),
    "UMID": (0.0, 100.0, "%"),
    "PLUV": (0.0, 300.0, "mm"),
    "PRES": (850.0, 1100.0, "hPa"),
    "VENT": (0.0, 60.0, "m/s"),
}

#: Catálogo de eventos conhecidos (ER-05 aceita qualquer código bem formado).
CATALOGO_ALERTAS = {
    "CHUVA",
    "CHUVA_FORTE",
    "VENDAVAL",
    "VENDAVAL_COM_DESCARGAS",
    "MARE_ALTA_DE_SIZIGIA",
    "CALOR",
    "ESTIAGEM",
}

NOMES_DOS_CAMPOS = [
    ("código da estação", ER01),
    ("carimbo temporal", ER02),
    ("coordenadas", ER04),
    ("leituras dos sensores", ER03),
    ("versão de firmware", ER06),
    ("alerta", ER05),
]


# ---------------------------------------------------------------------------
# Estruturas de saída
# ---------------------------------------------------------------------------


@dataclass
class Leitura:
    grandeza: str
    valor: float
    unidade: str
    suspeita: bool = False

    def __str__(self) -> str:
        marca = " (fora da faixa esperada)" if self.suspeita else ""
        return f"{self.grandeza} = {self.valor} {self.unidade}{marca}"


@dataclass
class Registro:
    numero_da_linha: int
    codigo_estacao: str
    sub_estacao: str | None
    instante: datetime
    latitude: float
    longitude: float
    leituras: list[Leitura]
    firmware: str
    versao: tuple[int, int, int]
    pre_lancamento: str | None
    alerta_nivel: int | None = None
    alerta_codigo: str | None = None
    avisos: list[str] = field(default_factory=list)

    @property
    def estavel(self) -> bool:
        return self.pre_lancamento is None


@dataclass
class LinhaInvalida:
    numero_da_linha: int
    conteudo: str
    mensagens: list[str]


@dataclass
class ResultadoAnalise:
    registros: list[Registro] = field(default_factory=list)
    invalidas: list[LinhaInvalida] = field(default_factory=list)
    linhas_lidas: int = 0
    linhas_ignoradas: int = 0

    @property
    def total_processadas(self) -> int:
        return len(self.registros) + len(self.invalidas)

    @property
    def taxa_de_acerto(self) -> float:
        if self.total_processadas == 0:
            return 0.0
        return 100.0 * len(self.registros) / self.total_processadas


class ErroDeEntrada(Exception):
    """Entrada ausente, vazia ou ilegível — sempre com mensagem ao usuário."""


# ---------------------------------------------------------------------------
# Análise de campos
# ---------------------------------------------------------------------------


def _analisar_codigo(campo: str, erros: list[str]) -> tuple[str, str | None]:
    if not ER01.aceita(campo):
        erros.append(
            f"Campo 1 (código da estação): '{campo}' não casa com {ER01.sintaxe}"
        )
        return campo, None
    if "." in campo:
        base, sub = campo.split(".", 1)
        return base, sub
    return campo, None


def _analisar_instante(campo: str, erros: list[str], avisos: list[str]):
    if not ER02.aceita(campo):
        erros.append(
            f"Campo 2 (carimbo temporal): '{campo}' não casa com {ER02.sintaxe}"
        )
        return None
    texto = campo[:-1] + "+00:00" if campo.endswith("Z") else campo
    try:
        return datetime.fromisoformat(texto)
    except ValueError:
        erros.append(
            f"Campo 2 (carimbo temporal): '{campo}' tem forma válida, "
            "mas não corresponde a uma data real do calendário."
        )
        return None


def _analisar_coordenadas(campo: str, erros: list[str], avisos: list[str]):
    if not ER04.aceita(campo):
        erros.append(
            f"Campo 3 (coordenadas): '{campo}' não casa com {ER04.sintaxe}"
        )
        return None
    latitude, longitude = (float(p) for p in campo.split(","))
    if abs(latitude) > 90 or abs(longitude) > 180:
        erros.append(
            f"Campo 3 (coordenadas): '{campo}' está fora da faixa geográfica "
            "válida (|lat| ≤ 90 e |lon| ≤ 180)."
        )
        return None
    return latitude, longitude


def _analisar_leituras(campo: str, erros: list[str], avisos: list[str]):
    leituras: list[Leitura] = []
    if campo.strip() == "":
        erros.append("Campo 4 (leituras): nenhum par grandeza=valor foi informado.")
        return leituras
    for item in campo.split(SEPARADOR_LEITURAS):
        item = item.strip()
        if not ER03.aceita(item):
            erros.append(
                f"Campo 4 (leituras): '{item}' não casa com {ER03.sintaxe}"
            )
            continue
        casamento = _EXTRATOR_LEITURA.fullmatch(item)
        grandeza = casamento.group("grandeza")
        valor = float(casamento.group("valor"))
        unidade = casamento.group("unidade")
        leitura = Leitura(grandeza, valor, unidade)
        faixa = FAIXAS_PLAUSIVEIS.get(grandeza)
        if faixa is None:
            avisos.append(f"Grandeza '{grandeza}' não faz parte do catálogo de sensores.")
        else:
            minimo, maximo, unidade_esperada = faixa
            if unidade != unidade_esperada:
                avisos.append(
                    f"{grandeza} deveria ser medida em '{unidade_esperada}', "
                    f"e não em '{unidade}'."
                )
            if not (minimo <= valor <= maximo):
                leitura.suspeita = True
                avisos.append(
                    f"{grandeza} = {valor}{unidade} está fora da faixa "
                    f"[{minimo}, {maximo}]."
                )
        leituras.append(leitura)
    return leituras


def _analisar_firmware(campo: str, erros: list[str]):
    if not ER06.aceita(campo):
        erros.append(
            f"Campo 5 (firmware): '{campo}' não casa com {ER06.sintaxe}"
        )
        return None, None
    corpo = campo[len("fw-v"):]
    rotulo = None
    if "-" in corpo:
        corpo, rotulo = corpo.split("-", 1)
        rotulo = rotulo.split(".", 1)[0]
    maior, menor, correcao = (int(p) for p in corpo.split("."))
    return (maior, menor, correcao), rotulo


def _analisar_alerta(campo: str, erros: list[str], avisos: list[str]):
    if not ER05.aceita(campo):
        erros.append(f"Campo 6 (alerta): '{campo}' não casa com {ER05.sintaxe}")
        return None, None
    _, _, resto = campo.partition("!ALERTA:NIVEL")
    nivel, _, codigo = resto.partition(":")
    if codigo not in CATALOGO_ALERTAS:
        avisos.append(f"Código de alerta '{codigo}' não consta do catálogo.")
    return int(nivel), codigo


# ---------------------------------------------------------------------------
# Análise de linha e de arquivo
# ---------------------------------------------------------------------------


def analisar_linha(linha: str, numero: int = 1) -> Registro | LinhaInvalida:
    """Analisa uma linha de telemetria e devolve um Registro ou uma LinhaInvalida."""
    if linha is None:
        return LinhaInvalida(numero, "", ["Linha inexistente (valor nulo)."])
    bruta = linha.strip()
    if bruta == "":
        return LinhaInvalida(numero, "", ["Linha vazia: nada a analisar."])

    erros: list[str] = []
    avisos: list[str] = []
    campos = [c.strip() for c in bruta.split(SEPARADOR_CAMPOS)]

    if len(campos) not in (5, 6):
        return LinhaInvalida(
            numero,
            bruta,
            [
                f"Esperados 5 ou 6 campos separados por '{SEPARADOR_CAMPOS}', "
                f"mas foram encontrados {len(campos)}."
            ],
        )

    codigo, sub = _analisar_codigo(campos[0], erros)
    instante = _analisar_instante(campos[1], erros, avisos)
    posicao = _analisar_coordenadas(campos[2], erros, avisos)
    leituras = _analisar_leituras(campos[3], erros, avisos)
    versao, rotulo = _analisar_firmware(campos[4], erros)

    nivel = codigo_alerta = None
    if len(campos) == 6:
        if campos[5] == "":
            erros.append("Campo 6 (alerta): campo presente, porém vazio.")
        else:
            nivel, codigo_alerta = _analisar_alerta(campos[5], erros, avisos)

    if erros or instante is None or posicao is None or versao is None:
        return LinhaInvalida(numero, bruta, erros or ["Registro incompleto."])

    return Registro(
        numero_da_linha=numero,
        codigo_estacao=codigo,
        sub_estacao=sub,
        instante=instante,
        latitude=posicao[0],
        longitude=posicao[1],
        leituras=leituras,
        firmware=campos[4],
        versao=versao,
        pre_lancamento=rotulo,
        alerta_nivel=nivel,
        alerta_codigo=codigo_alerta,
        avisos=avisos,
    )


def analisar_texto(texto: str) -> ResultadoAnalise:
    """Analisa um bloco de texto com vários registros (um por linha)."""
    if texto is None or texto.strip() == "":
        raise ErroDeEntrada(
            "Nenhum conteúdo foi fornecido: a entrada está vazia ou só contém "
            "espaços em branco."
        )

    resultado = ResultadoAnalise()
    for numero, linha in enumerate(texto.splitlines(), start=1):
        resultado.linhas_lidas += 1
        despida = linha.strip()
        if despida == "" or despida.startswith(MARCA_COMENTARIO):
            resultado.linhas_ignoradas += 1
            continue
        analisada = analisar_linha(linha, numero)
        if isinstance(analisada, Registro):
            resultado.registros.append(analisada)
        else:
            resultado.invalidas.append(analisada)

    if resultado.total_processadas == 0:
        raise ErroDeEntrada(
            "O conteúdo informado não possui nenhuma linha de telemetria "
            "(apenas linhas vazias ou comentários iniciados por '#')."
        )
    return resultado


def analisar_arquivo(caminho: str | Path) -> ResultadoAnalise:
    """Lê e analisa um arquivo de telemetria, com mensagens claras de erro."""
    if caminho is None or str(caminho).strip() == "":
        raise ErroDeEntrada("Informe o caminho de um arquivo de telemetria.")
    arquivo = Path(caminho)
    if not arquivo.exists():
        raise ErroDeEntrada(f"Arquivo não encontrado: '{arquivo}'.")
    if arquivo.is_dir():
        raise ErroDeEntrada(f"'{arquivo}' é um diretório, não um arquivo de log.")
    try:
        texto = arquivo.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise ErroDeEntrada(
            f"'{arquivo}' não está em UTF-8 e não pôde ser lido como texto."
        ) from None
    if texto.strip() == "":
        raise ErroDeEntrada(f"O arquivo '{arquivo}' está vazio.")
    return analisar_texto(texto)


# ---------------------------------------------------------------------------
# Estatísticas
# ---------------------------------------------------------------------------


def estatisticas_por_grandeza(resultado: ResultadoAnalise) -> dict[str, dict[str, float]]:
    acumulado: dict[str, list[float]] = {}
    unidades: dict[str, str] = {}
    for registro in resultado.registros:
        for leitura in registro.leituras:
            acumulado.setdefault(leitura.grandeza, []).append(leitura.valor)
            unidades[leitura.grandeza] = leitura.unidade
    resumo = {}
    for grandeza, valores in sorted(acumulado.items()):
        resumo[grandeza] = {
            "amostras": len(valores),
            "minimo": min(valores),
            "maximo": max(valores),
            "media": round(sum(valores) / len(valores), 2),
            "unidade": unidades[grandeza],
        }
    return resumo


def contagem_de_alertas(resultado: ResultadoAnalise) -> dict[int, int]:
    contagem: dict[int, int] = {}
    for registro in resultado.registros:
        if registro.alerta_nivel is not None:
            contagem[registro.alerta_nivel] = contagem.get(registro.alerta_nivel, 0) + 1
    return dict(sorted(contagem.items()))


def estacoes(resultado: ResultadoAnalise) -> dict[str, int]:
    contagem: dict[str, int] = {}
    for registro in resultado.registros:
        contagem[registro.codigo_estacao] = contagem.get(registro.codigo_estacao, 0) + 1
    return dict(sorted(contagem.items()))


def firmwares(resultado: ResultadoAnalise) -> dict[str, int]:
    contagem: dict[str, int] = {}
    for registro in resultado.registros:
        contagem[registro.firmware] = contagem.get(registro.firmware, 0) + 1
    return dict(sorted(contagem.items()))
