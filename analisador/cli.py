"""
Módulo `cli`
============

Interface com o usuário: modo por argumentos de linha de comando e modo
interativo por menu. Todas as entradas inválidas (arquivo inexistente, cadeia
vazia, identificador desconhecido, opção fora do menu) produzem mensagens
explicativas, nunca rastreamentos de exceção.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from . import relatorio as rel
from .expressoes import FICHAS, FICHAS_POR_ID, obter_ficha
from .processador import ErroDeEntrada, analisar_arquivo, analisar_linha, Registro

RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO_PADRAO = RAIZ / "dados" / "telemetria_setembro.log"

BANNER = r"""
 __  __      _         ___
|  \/  |___ | |_ ___  | _ \___ __ _ _____ __
| |\/| / -_)|  _/ -_) |   / -_) _` / -_) \ /
|_|  |_\___| \__\___| |_|_\___\__, \___/_\_\
  MeteoRegex - analisador de  |___/ telemetria
  Linguagens Formais e Autômatos - 1o bimestre
"""


# ---------------------------------------------------------------------------
# Ações
# ---------------------------------------------------------------------------


def acao_arquivo(caminho, detalhar: bool = False) -> int:
    try:
        resultado = analisar_arquivo(caminho)
    except ErroDeEntrada as erro:
        print(f"[ERRO DE ENTRADA] {erro}")
        return 2
    print(rel.relatorio_da_analise(resultado, detalhar=detalhar))
    return 0


def acao_linha(texto: str) -> int:
    if texto is None or texto.strip() == "":
        print("[ERRO DE ENTRADA] Nenhuma linha foi informada para análise.")
        return 2
    analisada = analisar_linha(texto, numero=1)
    if isinstance(analisada, Registro):
        print("Registro VÁLIDO.")
        sub = f" (sub-estação {analisada.sub_estacao})" if analisada.sub_estacao else ""
        print(f"  estação   : {analisada.codigo_estacao}{sub}")
        print(f"  instante  : {analisada.instante.isoformat()}")
        print(f"  posição   : {analisada.latitude}, {analisada.longitude}")
        print(f"  firmware  : {analisada.firmware} "
              f"({'estável' if analisada.estavel else analisada.pre_lancamento})")
        for leitura in analisada.leituras:
            print(f"  leitura   : {leitura}")
        if analisada.alerta_codigo:
            print(f"  alerta    : nível {analisada.alerta_nivel} — {analisada.alerta_codigo}")
        for aviso in analisada.avisos:
            print(f"  aviso     : {aviso}")
        return 0
    print("Registro INVÁLIDO.")
    for mensagem in analisada.mensagens:
        print(f"  ↳ {mensagem}")
    return 1


def acao_validar(identificador: str, cadeia: str, trilha: bool = False) -> int:
    try:
        ficha = obter_ficha(identificador)
    except KeyError as erro:
        print(f"[ERRO DE ENTRADA] {erro.args[0]}")
        return 2
    if cadeia is None or cadeia == "":
        print("[AVISO] Cadeia vazia (ε). Nenhuma das ER do projeto aceita ε, "
              "pois todas exigem pelo menos um símbolo.")
    print(rel.relatorio_de_validacao(ficha, cadeia or "", com_trilha=trilha))
    return 0


def acao_fichas(identificador: str | None = None, com_automato: bool = False) -> int:
    if identificador:
        try:
            ficha = obter_ficha(identificador)
        except KeyError as erro:
            print(f"[ERRO DE ENTRADA] {erro.args[0]}")
            return 2
        print(rel.ficha_em_texto(ficha, com_automato=com_automato))
        return 0
    print(rel.todas_as_fichas(com_automato=com_automato))
    return 0


def acao_bateria() -> int:
    """Executa, em tela, a bateria de cadeias aceitas/rejeitadas de cada ER."""
    from .automatos import obter_automato

    falhas = 0
    for ficha in FICHAS:
        automato = obter_automato(ficha.identificacao)
        print(rel.subtitulo(f"{ficha.identificacao} — {ficha.nome}"))
        for cadeia, esperado in (
            [(c, True) for c in ficha.aceitas] + [(c, False) for c in ficha.rejeitadas]
        ):
            por_er = ficha.aceita(cadeia)
            por_afne = automato.aceita(cadeia)
            ok = (por_er == esperado) and (por_afne == esperado)
            falhas += 0 if ok else 1
            simbolo = "✓" if ok else "✗"
            print(
                f"  {simbolo} {'aceita   ' if esperado else 'rejeitada'} "
                f"| ER={'S' if por_er else 'N'} AFNε={'S' if por_afne else 'N'} "
                f"| {cadeia!r}"
            )
    print()
    if falhas:
        print(f"{falhas} caso(s) divergente(s).")
        return 1
    print("Todos os casos de teste se comportaram como o esperado, "
          "com ER e AFNε em pleno acordo.")
    return 0


# ---------------------------------------------------------------------------
# Modo interativo
# ---------------------------------------------------------------------------

MENU = """
Escolha uma opção:
  1 - Analisar o arquivo de exemplo
  2 - Analisar outro arquivo de telemetria
  3 - Analisar uma única linha digitada
  4 - Testar uma cadeia contra uma Expressão Regular
  5 - Exibir as fichas das Expressões Regulares
  6 - Exibir a descrição formal de um AFNε
  7 - Executar a bateria de casos de teste
  0 - Sair
"""


def _perguntar(rotulo: str) -> str:
    try:
        return input(rotulo).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return "0"


def modo_interativo() -> int:
    print(BANNER)
    while True:
        print(MENU)
        opcao = _perguntar("opção> ")
        if opcao == "0":
            print("Encerrando. Até a próxima!")
            return 0
        if opcao == "1":
            acao_arquivo(ARQUIVO_PADRAO, detalhar=False)
        elif opcao == "2":
            acao_arquivo(_perguntar("caminho do arquivo> "))
        elif opcao == "3":
            acao_linha(_perguntar("linha de telemetria> "))
        elif opcao == "4":
            identificador = _perguntar(f"ER ({', '.join(FICHAS_POR_ID)})> ")
            cadeia = _perguntar("cadeia> ")
            acao_validar(identificador, cadeia, trilha=True)
        elif opcao == "5":
            acao_fichas(_perguntar("ER (ENTER para todas)> ") or None)
        elif opcao == "6":
            from .automatos import obter_automato

            identificador = _perguntar(f"ER ({', '.join(FICHAS_POR_ID)})> ")
            try:
                print(obter_automato(identificador).formal())
            except KeyError as erro:
                print(f"[ERRO DE ENTRADA] {erro.args[0]}")
        elif opcao == "7":
            acao_bateria()
        else:
            print(f"[ERRO DE ENTRADA] Opção '{opcao}' inexistente. "
                  "Digite um número de 0 a 7.")


# ---------------------------------------------------------------------------
# Argumentos
# ---------------------------------------------------------------------------


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="meteoregex",
        description="Analisador de telemetria de estações meteorológicas "
                    "baseado em Expressões Regulares e AFNε.",
        epilog="Sem argumentos, o programa entra no modo interativo.",
    )
    parser.add_argument("-a", "--arquivo", help="arquivo de telemetria a analisar")
    parser.add_argument("-l", "--linha", help="analisa uma única linha de telemetria")
    parser.add_argument("-e", "--er", help="identificador da ER (ex.: ER-03)")
    parser.add_argument("-c", "--cadeia", help="cadeia a testar contra a ER indicada")
    parser.add_argument("-f", "--fichas", action="store_true",
                        help="exibe as fichas das Expressões Regulares")
    parser.add_argument("-t", "--testes", action="store_true",
                        help="executa a bateria de cadeias aceitas/rejeitadas")
    parser.add_argument("-d", "--detalhar", action="store_true",
                        help="lista também cada registro válido")
    parser.add_argument("--afne", action="store_true",
                        help="inclui a descrição formal dos AFNε nas fichas")
    return parser


def principal(argumentos: list[str] | None = None) -> int:
    parser = construir_parser()
    args = parser.parse_args(argumentos)

    if args.testes:
        return acao_bateria()
    if args.fichas:
        return acao_fichas(args.er, com_automato=args.afne)
    if args.cadeia is not None:
        if not args.er:
            print("[ERRO DE ENTRADA] Informe também a ER com -e (ex.: -e ER-03).")
            return 2
        return acao_validar(args.er, args.cadeia, trilha=True)
    if args.linha is not None:
        return acao_linha(args.linha)
    if args.arquivo is not None:
        return acao_arquivo(args.arquivo, detalhar=args.detalhar)
    return modo_interativo()
