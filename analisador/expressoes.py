"""
Módulo `expressoes`
===================

Fonte única de verdade das Expressões Regulares do projeto **MeteoRegex**.

Cada Expressão Regular é declarada **uma única vez**, como uma constante de
string bruta (`r"..."`). A mesma constante é usada:

  * pelo validador (`re.fullmatch`);
  * pela ficha de documentação (campo `sintaxe`);
  * pelos testes automatizados;
  * pelos geradores de documentação, diagramas e relatório.

Dessa forma a sintaxe exibida nos slides/relatório é, por construção,
exatamente aquela executada pelo programa (exigência do guia de sintaxe).

Restrições de projeto (item 4 do guia):
  * não são usadas retroreferências (\\1), recursão, condicionais ou lookaround;
  * todos os agrupamentos são *não capturantes* `(?:r)`, pois servem apenas
    para definir precedência — equivalem ao agrupamento formal `( r )`;
  * a validação é sempre de cadeia inteira, via `re.fullmatch`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# 1. Padrões — sintaxe exatamente como executada pelo programa
# ---------------------------------------------------------------------------

PADRAO_CODIGO_ESTACAO = r"[A-Z]{2}-[A-Z]{3}-[0-9]{3}[A-Z](?:\.[0-9]{1,2})?"

PADRAO_CARIMBO_TEMPORAL = (
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]{1,3})?(?:Z|[+-][0-9]{2}:[0-9]{2})?"
)

PADRAO_LEITURA_SENSOR = r"[A-Z]{3,4}=[+-]?[0-9]+(?:\.[0-9]+)?(?:C|%|mm|hPa|m/s)"

PADRAO_COORDENADA = r"[+-]?[0-9]{1,3}\.[0-9]{4,6},[+-]?[0-9]{1,3}\.[0-9]{4,6}"

PADRAO_ALERTA = r"!ALERTA:NIVEL[1-3]:[A-Z]+(?:_[A-Z]+)*"

PADRAO_FIRMWARE = r"fw-v[0-9]+(?:\.[0-9]+){2}(?:-(?:alpha|beta|rc)\.[0-9]+)?"

# Padrão auxiliar de EXTRAÇÃO (não avaliado como ER do trabalho).
# Reconhece exatamente a mesma linguagem de PADRAO_LEITURA_SENSOR; a única
# diferença é que os grupos passam de não capturantes para nomeados, o que
# não altera o conjunto de cadeias aceitas.
PADRAO_LEITURA_EXTRACAO = (
    r"(?P<grandeza>[A-Z]{3,4})=(?P<valor>[+-]?[0-9]+(?:\.[0-9]+)?)"
    r"(?P<unidade>C|%|mm|hPa|m/s)"
)


# ---------------------------------------------------------------------------
# 2. Ficha obrigatória (seção 5 do guia de sintaxe)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FichaER:
    """Ficha de documentação de uma Expressão Regular."""

    identificacao: str          # ER-01 ... ER-06
    nome: str                   # nome curto
    finalidade: str             # função dentro do programa
    alfabeto: str               # Σ
    linguagem: str              # descrição precisa de L
    er_formal: str              # notação algébrica da disciplina
    sintaxe: str                # padrão copiado do código-fonte
    equivalencia: list[str]     # atalho computacional -> operador formal
    operadores: list[str]       # explicação dos operadores usados
    aceitas: list[str]          # >= 6 cadeias aceitas
    rejeitadas: list[str]       # >= 6 cadeias rejeitadas
    caso_limite: str            # descrição do(s) caso(s)-limite
    resultado_e_limite: str     # comportamento observado e limitações
    campo_do_registro: str = "" # em que campo do log a ER é aplicada
    exemplos_extra: dict[str, str] = field(default_factory=dict)

    # -- operações -----------------------------------------------------------
    @property
    def regex(self) -> re.Pattern[str]:
        return re.compile(self.sintaxe)

    def aceita(self, cadeia: str) -> bool:
        """Verdadeiro se a cadeia INTEIRA pertence à linguagem."""
        if cadeia is None:
            return False
        return self.regex.fullmatch(cadeia) is not None


# ---------------------------------------------------------------------------
# 3. As seis fichas
# ---------------------------------------------------------------------------

_ALFA_MAIUSC = "M = {A, B, ..., Z}"
_DIGITO = "D = {0, 1, ..., 9}"

ER01 = FichaER(
    identificacao="ER-01",
    nome="Código de estação meteorológica",
    finalidade=(
        "Validar o identificador da estação que originou o registro e permitir "
        "agrupar as leituras por estação e por sub-estação."
    ),
    campo_do_registro="campo 1 do registro de telemetria",
    alfabeto=f"Σ₁ = M ∪ D ∪ {{ '-', '.' }}, com {_ALFA_MAIUSC} e {_DIGITO}",
    linguagem=(
        "Cadeias formadas por duas letras maiúsculas (sigla da UF), um hífen, "
        "três letras maiúsculas (código do município), um hífen, três dígitos "
        "(número sequencial da estação) e uma letra maiúscula (revisão do "
        "hardware), seguidas opcionalmente de um ponto e de um ou dois dígitos "
        "que identificam a sub-estação."
    ),
    er_formal=(
        "M M - M M M - D D D M ( . D ( D | ε ) | ε )\n"
        "forma abreviada: M{2} - M{3} - D{3} M ( . D{1,2} )?"
    ),
    sintaxe=PADRAO_CODIGO_ESTACAO,
    equivalencia=[
        "[A-Z]  ≡  (A | B | ... | Z)  = classe M",
        "[0-9]  ≡  (0 | 1 | ... | 9)  = classe D",
        "r{2}   ≡  r r   (concatenação de 2 cópias)",
        "r{3}   ≡  r r r (concatenação de 3 cópias)",
        "r{1,2} ≡  (r | r r)",
        "(?:r)? ≡  ( r | ε )",
        r"\.     ≡  símbolo literal '.' (o escape remove o significado especial)",
    ],
    operadores=[
        "concatenação: impõe a ordem rígida dos blocos do identificador;",
        "classe/intervalo: abreviação da união dos símbolos do alfabeto;",
        "repetição exata {m}: concatenação de m cópias;",
        "repetição limitada {1,2}: união de uma e de duas cópias;",
        "opcionalidade ?: união com a palavra vazia ε (sufixo de sub-estação).",
    ],
    aceitas=[
        "PA-BEL-004A",
        "PA-ANA-127B",
        "AM-MAO-001A",
        "PA-BEL-004A.2",
        "RJ-RIO-999Z.15",
        "SP-SAO-000A.1",
    ],
    rejeitadas=[
        "pa-bel-004a",       # letras minúsculas
        "PA-BE-004A",        # apenas 2 letras no código do município
        "PA-BEL-04A",        # apenas 2 dígitos
        "PA-BEL-004",        # falta a letra de revisão
        "PA-BEL-004A.",      # ponto sem dígito (caso-limite)
        "PA-BEL-004A.123",   # três dígitos de sub-estação
    ],
    caso_limite=(
        "\"PA-BEL-004A.\" — prefixo válido seguido do ponto sem nenhum dígito: "
        "o fecho opcional exige que, havendo o ponto, exista ao menos um dígito. "
        "Caso-limite oposto: \"PA-BEL-004A\" (sufixo ausente, ramo ε) é aceito."
    ),
    resultado_e_limite=(
        "A ER valida apenas a FORMA do código. Não verifica se a sigla é uma UF "
        "existente nem se a estação está cadastrada: \"ZZ-XXX-000A\" é "
        "formalmente aceita. Essa verificação semântica é feita depois, por "
        "consulta à lista de estações conhecidas."
    ),
)

ER02 = FichaER(
    identificacao="ER-02",
    nome="Carimbo temporal ISO-8601",
    finalidade=(
        "Validar o instante da coleta, com fração de segundo e fuso horário "
        "opcionais, permitindo ordenar cronologicamente os registros."
    ),
    campo_do_registro="campo 2 do registro de telemetria",
    alfabeto=f"Σ₂ = D ∪ {{ '-', 'T', ':', '.', 'Z', '+' }}, com {_DIGITO}",
    linguagem=(
        "Cadeias no formato AAAA-MM-DDThh:mm:ss, opcionalmente seguidas de um "
        "ponto e de 1 a 3 dígitos (milissegundos) e, opcionalmente, de um "
        "indicador de fuso: a letra Z (UTC) ou um sinal seguido de hh:mm."
    ),
    er_formal=(
        "D{4} - D{2} - D{2} T D{2} : D{2} : D{2} "
        "( . D ( D ( D | ε ) | ε ) | ε ) ( Z | ( + | - ) D{2} : D{2} | ε )"
    ),
    sintaxe=PADRAO_CARIMBO_TEMPORAL,
    equivalencia=[
        "[0-9]     ≡ (0 | 1 | ... | 9) = classe D",
        "r{4}      ≡ r r r r",
        "r{1,3}    ≡ (r | r r | r r r)",
        "[+-]      ≡ (+ | -)  — dentro da classe o '-' está na borda e é literal",
        "(?:r)?    ≡ ( r | ε )",
        "(?:a|b)   ≡ união a | b",
    ],
    operadores=[
        "concatenação: fixa a ordem data → 'T' → hora;",
        "repetição exata {m}: blocos de tamanho fixo (ano, mês, dia, hora…);",
        "repetição limitada {1,3}: fração de segundo de 1 a 3 dígitos;",
        "união |: escolhe entre fuso 'Z' e deslocamento ±hh:mm;",
        "opcionalidade ?: dois sufixos independentes podem ser ε.",
    ],
    aceitas=[
        "2026-09-21T14:35:02",
        "2026-09-21T14:35:02Z",
        "2026-09-21T14:35:02.5",
        "2026-09-21T14:35:02.123-03:00",
        "2026-01-01T00:00:00+00:00",
        "1999-12-31T23:59:59.999Z",
    ],
    rejeitadas=[
        "2026-09-21 14:35:02",      # espaço no lugar do separador T
        "26-09-21T14:35:02",        # ano com 2 dígitos
        "2026-09-21T14:35",         # faltam os segundos
        "2026-09-21T14:35:02.",     # ponto sem dígitos (caso-limite)
        "2026-09-21T14:35:02.1234", # 4 dígitos de fração
        "2026-09-21T14:35:02-0300", # deslocamento sem ':'
    ],
    caso_limite=(
        "\"2026-09-21T14:35:02.\" — a parte obrigatória está completa, mas o "
        "ponto abre uma fração vazia; como {1,3} exige pelo menos um dígito, a "
        "cadeia é rejeitada. O caso-limite aceito correspondente é "
        "\"2026-09-21T14:35:02\" (ambos os sufixos opcionais em ε)."
    ),
    resultado_e_limite=(
        "A ER reconhece a ESTRUTURA do carimbo, não a validade do calendário: "
        "\"2026-13-45T99:99:99\" é aceita pela ER. Datas impossíveis são "
        "descartadas na etapa seguinte, por conversão com datetime."
    ),
)

ER03 = FichaER(
    identificacao="ER-03",
    nome="Leitura de sensor com unidade",
    finalidade=(
        "Validar e extrair cada par grandeza=valor+unidade produzido pelos "
        "sensores da estação, base de todo o cálculo estatístico do programa."
    ),
    campo_do_registro="campo 4 do registro (itens separados por ';')",
    alfabeto=(
        "Σ₃ = M ∪ D ∪ { '=', '+', '-', '.', '%', 'm', 'h', 'P', 'a', '/', 's', 'C' }"
    ),
    linguagem=(
        "Cadeias compostas por uma sigla de 3 ou 4 letras maiúsculas, o símbolo "
        "'=', um número decimal com sinal opcional e parte fracionária "
        "opcional, e uma unidade pertencente a { C, %, mm, hPa, m/s }."
    ),
    er_formal=(
        "M M M ( M | ε ) = ( + | - | ε ) D D* ( . D D* | ε ) "
        "( C | % | m m | h P a | m / s )"
    ),
    sintaxe=PADRAO_LEITURA_SENSOR,
    equivalencia=[
        "[A-Z]{3,4} ≡ M M M ( M | ε )",
        "[+-]?      ≡ ( + | - | ε )",
        "[0-9]+     ≡ D D*  (fecho positivo = uma cópia seguida do fecho de Kleene)",
        r"(?:\.[0-9]+)? ≡ ( . D D* | ε )",
        "(?:C|%|mm|hPa|m/s) ≡ união de cinco cadeias literais",
    ],
    operadores=[
        "fecho positivo +: a parte inteira tem pelo menos um dígito;",
        "fecho de Kleene *: implícito na expansão de + (D D*);",
        "opcionalidade ?: sinal e parte fracionária podem ser ε;",
        "união |: escolhe a unidade de medida;",
        "concatenação: amarra sigla, '=', número e unidade.",
    ],
    aceitas=[
        "TEMP=+27.4C",
        "UMID=85%",
        "PLUV=0.0mm",
        "PRES=1012.75hPa",
        "VENT=3.2m/s",
        "TEMP=-0C",
    ],
    rejeitadas=[
        "TEMP=27.4",       # sem unidade
        "TE=27C",          # sigla com 2 letras
        "TEMPER=27C",      # sigla com 6 letras
        "TEMP=.5C",        # sem parte inteira (caso-limite)
        "TEMP=27.C",       # ponto sem dígitos após ele
        "temp=27C",        # sigla minúscula
    ],
    caso_limite=(
        "\"TEMP=.5C\" — número sem parte inteira: o fecho positivo [0-9]+ exige "
        "ao menos um dígito antes do ponto, logo a cadeia é rejeitada. O "
        "caso-limite aceito é \"TEMP=-0C\", número mínimo com sinal e sem "
        "parte fracionária."
    ),
    resultado_e_limite=(
        "A ER não impõe faixa física: \"TEMP=+999.9C\" é aceita. A checagem de "
        "plausibilidade (faixas por grandeza) é feita no módulo processador, "
        "que sinaliza a leitura como suspeita sem invalidar o registro."
    ),
)

ER04 = FichaER(
    identificacao="ER-04",
    nome="Par de coordenadas geodésicas decimais",
    finalidade=(
        "Validar a posição informada pela estação (latitude e longitude em "
        "graus decimais com sinal), usada no agrupamento geográfico do relatório."
    ),
    campo_do_registro="campo 3 do registro de telemetria",
    alfabeto=f"Σ₄ = D ∪ {{ '+', '-', '.', ',' }}, com {_DIGITO}",
    linguagem=(
        "Dois números decimais separados por vírgula; cada número possui sinal "
        "opcional, de 1 a 3 dígitos inteiros, ponto obrigatório e de 4 a 6 "
        "casas decimais."
    ),
    er_formal=(
        "N , N, onde N = ( + | - | ε ) D ( D ( D | ε ) | ε ) . "
        "D D D D ( D ( D | ε ) | ε )\n"
        "forma abreviada: N = ( + | - )? D{1,3} . D{4,6}"
    ),
    sintaxe=PADRAO_COORDENADA,
    equivalencia=[
        "[+-]?      ≡ ( + | - | ε )",
        "[0-9]{1,3} ≡ ( D | D D | D D D )",
        "[0-9]{4,6} ≡ ( D{4} | D{5} | D{6} )",
        r"\.         ≡ símbolo literal '.'",
        "','        ≡ símbolo literal ','",
    ],
    operadores=[
        "repetição limitada {m,n}: união das repetições de m até n cópias;",
        "opcionalidade ?: o sinal pode ser ε (coordenada positiva);",
        "concatenação: latitude, vírgula e longitude, nessa ordem;",
        "escape \\. : garante que o ponto seja símbolo do alfabeto e não o "
        "curinga do motor.",
    ],
    aceitas=[
        "-1.455833,-48.503889",
        "+1.4558,-48.5038",
        "0.0000,0.0000",
        "-23.550520,-46.633308",
        "90.000000,180.000000",
        "-1.4558,48.5038",
    ],
    rejeitadas=[
        "-1.455833",            # só a latitude
        "-1.45,-48.50",         # apenas 2 casas decimais (caso-limite)
        "-1455833,-48503889",   # sem ponto decimal
        "-1.455833;-48.503889", # separador errado
        "-1.4558333,-48.5038",  # 7 casas decimais
        "-1.4558, -48.5038",    # espaço após a vírgula
    ],
    caso_limite=(
        "\"-1.45,-48.50\" — coordenada plausível, porém com 2 casas decimais: "
        "a repetição {4,6} exige no mínimo 4, e a cadeia é rejeitada. O "
        "caso-limite aceito é \"0.0000,0.0000\" (mínimo de dígitos inteiros e "
        "de casas decimais, sem sinal)."
    ),
    resultado_e_limite=(
        "A ER não restringe a faixa geográfica: \"999.0000,999.0000\" seria "
        "aceita se tivesse 3 dígitos inteiros. A validação de faixa "
        "(|lat| ≤ 90, |lon| ≤ 180) é numérica e ocorre após o reconhecimento."
    ),
)

ER05 = FichaER(
    identificacao="ER-05",
    nome="Alerta hidrometeorológico",
    finalidade=(
        "Reconhecer o campo opcional de alerta, extraindo o nível de severidade "
        "e o código do evento para o painel de ocorrências."
    ),
    campo_do_registro="campo 6 (opcional) do registro de telemetria",
    alfabeto="Σ₅ = M ∪ { '!', ':', '_', '1', '2', '3' }, com M = {A, ..., Z}",
    linguagem=(
        "Cadeias iniciadas por \"!ALERTA:NIVEL\", seguidas de um dígito de 1 a "
        "3, de ':' e de um código formado por uma ou mais palavras de letras "
        "maiúsculas separadas por sublinhado."
    ),
    er_formal=(
        "! A L E R T A : N I V E L ( 1 | 2 | 3 ) : P ( _ P )*, "
        "onde P = M M*"
    ),
    sintaxe=PADRAO_ALERTA,
    equivalencia=[
        "'!ALERTA:NIVEL' ≡ concatenação de símbolos literais",
        "[1-3]  ≡ ( 1 | 2 | 3 )",
        "[A-Z]+ ≡ M M*  (fecho positivo)",
        "(?:_[A-Z]+)* ≡ ( _ M M* )*  (fecho de Kleene, inclui ε)",
    ],
    operadores=[
        "concatenação: prefixo fixo do alerta;",
        "intervalo [1-3]: união dos três níveis de severidade;",
        "fecho positivo +: cada palavra tem ao menos uma letra;",
        "fecho de Kleene *: zero ou mais palavras adicionais, o que inclui a "
        "palavra vazia ε (código de uma só palavra).",
    ],
    aceitas=[
        "!ALERTA:NIVEL1:CHUVA",
        "!ALERTA:NIVEL2:CHUVA_FORTE",
        "!ALERTA:NIVEL3:VENDAVAL_COM_DESCARGAS",
        "!ALERTA:NIVEL3:A",
        "!ALERTA:NIVEL2:MARE_ALTA_DE_SIZIGIA",
        "!ALERTA:NIVEL1:CALOR",
    ],
    rejeitadas=[
        "ALERTA:NIVEL1:CHUVA",       # sem '!'
        "!ALERTA:NIVEL4:CHUVA",      # nível fora de [1-3]
        "!ALERTA:NIVEL2:chuva",      # código minúsculo
        "!ALERTA:NIVEL2:",           # código vazio (caso-limite)
        "!ALERTA:NIVEL2:CHUVA_",     # sublinhado final sem palavra
        "!ALERTA:NIVEL2:CHUVA FORTE",# espaço não pertence a Σ₅
    ],
    caso_limite=(
        "\"!ALERTA:NIVEL2:\" — prefixo completo e código vazio: o fecho "
        "positivo [A-Z]+ impede a cadeia vazia, logo há rejeição. O "
        "caso-limite aceito é \"!ALERTA:NIVEL3:A\", com o menor código "
        "possível (uma única letra e o fecho de Kleene em ε)."
    ),
    resultado_e_limite=(
        "Qualquer código de evento em maiúsculas é aceito, inclusive códigos "
        "inexistentes no catálogo da Defesa Civil. O programa compara o código "
        "com um catálogo interno e marca como DESCONHECIDO quando não o encontra."
    ),
)

ER06 = FichaER(
    identificacao="ER-06",
    nome="Versão de firmware da estação",
    finalidade=(
        "Validar a versão do firmware embarcado e distinguir versões estáveis "
        "de versões de pré-lançamento no relatório de manutenção."
    ),
    campo_do_registro="campo 5 do registro de telemetria",
    alfabeto=(
        "Σ₆ = D ∪ { 'f', 'w', 'v', '-', '.', 'a', 'l', 'p', 'h', 'b', 'e', 't', "
        "'r', 'c' }"
    ),
    linguagem=(
        "Cadeias iniciadas pelo prefixo literal \"fw-v\", seguidas de três "
        "números inteiros separados por ponto (maior.menor.correção) e, "
        "opcionalmente, de um rótulo de pré-lançamento formado por '-', uma "
        "das palavras alpha, beta ou rc, um ponto e um número."
    ),
    er_formal=(
        "f w - v D D* ( . D D* ){2} "
        "( - ( a l p h a | b e t a | r c ) . D D* | ε )"
    ),
    sintaxe=PADRAO_FIRMWARE,
    equivalencia=[
        "'fw-v' ≡ concatenação de símbolos literais",
        "[0-9]+ ≡ D D*",
        r"(?:\.[0-9]+){2} ≡ ( . D D* ) ( . D D* )",
        "(?:alpha|beta|rc) ≡ união de três cadeias literais",
        "(?:...)? ≡ ( ... | ε )",
    ],
    operadores=[
        "concatenação: prefixo e blocos numéricos;",
        "fecho positivo +: cada número tem ao menos um dígito;",
        "repetição exata {2}: duplica o bloco '.número';",
        "união |: seleciona o tipo de pré-lançamento;",
        "opcionalidade ?: versões estáveis não possuem rótulo (ramo ε).",
    ],
    aceitas=[
        "fw-v3.11.2",
        "fw-v0.0.1",
        "fw-v12.0.45",
        "fw-v3.11.2-beta.4",
        "fw-v2.7.0-rc.1",
        "fw-v1.0.0-alpha.12",
    ],
    rejeitadas=[
        "fw-v3.11",           # apenas dois números (caso-limite)
        "fw-v3.11.2.4",       # quatro números
        "v3.11.2",            # sem o prefixo 'fw-'
        "fw-v3.11.2-beta",    # rótulo sem o número
        "fw-v3.11.2-gamma.1", # rótulo fora da união permitida
        "FW-V3.11.2",         # prefixo em maiúsculas
    ],
    caso_limite=(
        "\"fw-v3.11\" — versão com apenas dois componentes: a repetição exata "
        "{2} exige dois blocos '.número' após o primeiro número, e a cadeia é "
        "rejeitada. O caso-limite aceito é \"fw-v0.0.1\", a menor versão "
        "possível, com um dígito em cada bloco e sem rótulo."
    ),
    resultado_e_limite=(
        "A ER não compara versões: \"fw-v0.0.1\" e \"fw-v12.0.45\" são "
        "igualmente aceitas. A ordenação por recência é feita convertendo os "
        "blocos em inteiros após o reconhecimento."
    ),
)

FICHAS: list[FichaER] = [ER01, ER02, ER03, ER04, ER05, ER06]

FICHAS_POR_ID: dict[str, FichaER] = {f.identificacao: f for f in FICHAS}


# ---------------------------------------------------------------------------
# 4. Funções utilitárias
# ---------------------------------------------------------------------------


def obter_ficha(identificador: str) -> FichaER:
    """Recupera uma ficha por ``ER-0n`` ou pelo nome curto (ex.: ``ER-03``).

    Levanta ``KeyError`` com mensagem clara quando o identificador não existe.
    """
    chave = (identificador or "").strip().upper()
    if not chave:
        raise KeyError("Nenhum identificador de Expressão Regular foi informado.")
    if chave in FICHAS_POR_ID:
        return FICHAS_POR_ID[chave]
    disponiveis = ", ".join(FICHAS_POR_ID)
    raise KeyError(
        f"Expressão Regular '{identificador}' não existe. Disponíveis: {disponiveis}."
    )


def validar(identificador: str, cadeia: str) -> bool:
    """Testa se ``cadeia`` pertence à linguagem da ER indicada."""
    return obter_ficha(identificador).aceita(cadeia)
