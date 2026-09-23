"""
Módulo `relatorio`
==================

Responsável exclusivamente pela **saída** do programa: converte os resultados
produzidos pelo `processador` em texto legível no terminal. Manter a
formatação isolada permite reutilizar a análise em testes e em outras
interfaces sem duplicar código.
"""

from __future__ import annotations

from .automatos import obter_automato
from .expressoes import FICHAS, FichaER
from .processador import (
    ResultadoAnalise,
    contagem_de_alertas,
    estacoes,
    estatisticas_por_grandeza,
    firmwares,
)

LARGURA = 74


def titulo(texto: str) -> str:
    return f"\n{'═' * LARGURA}\n{texto.upper().center(LARGURA)}\n{'═' * LARGURA}"


def subtitulo(texto: str) -> str:
    return f"\n{texto}\n{'-' * len(texto)}"


# ---------------------------------------------------------------------------
# Relatório da análise de telemetria
# ---------------------------------------------------------------------------


def relatorio_da_analise(resultado: ResultadoAnalise, detalhar: bool = False) -> str:
    partes = [titulo("Relatório de análise da telemetria")]

    partes.append(subtitulo("1. Resumo"))
    partes.append(f"Linhas lidas ................. {resultado.linhas_lidas}")
    partes.append(f"Linhas ignoradas ............. {resultado.linhas_ignoradas} "
                  "(vazias ou comentários)")
    partes.append(f"Registros válidos ............ {len(resultado.registros)}")
    partes.append(f"Registros inválidos .......... {len(resultado.invalidas)}")
    partes.append(f"Taxa de aproveitamento ....... {resultado.taxa_de_acerto:.1f}%")

    partes.append(subtitulo("2. Estações identificadas (ER-01)"))
    contagem = estacoes(resultado)
    if contagem:
        for codigo, quantidade in contagem.items():
            partes.append(f"  {codigo:<16} {quantidade} registro(s)")
    else:
        partes.append("  Nenhuma estação válida encontrada.")

    partes.append(subtitulo("3. Estatísticas por grandeza (ER-03)"))
    resumo = estatisticas_por_grandeza(resultado)
    if resumo:
        partes.append(f"  {'Grandeza':<10}{'N':>4}{'Mínimo':>12}{'Média':>12}"
                      f"{'Máximo':>12}  Unidade")
        for grandeza, dados in resumo.items():
            partes.append(
                f"  {grandeza:<10}{dados['amostras']:>4}{dados['minimo']:>12.2f}"
                f"{dados['media']:>12.2f}{dados['maximo']:>12.2f}  {dados['unidade']}"
            )
    else:
        partes.append("  Nenhuma leitura válida encontrada.")

    partes.append(subtitulo("4. Alertas (ER-05)"))
    alertas = contagem_de_alertas(resultado)
    if alertas:
        for nivel, quantidade in alertas.items():
            partes.append(f"  Nível {nivel}: {quantidade} ocorrência(s)")
        for registro in resultado.registros:
            if registro.alerta_codigo:
                partes.append(
                    f"    linha {registro.numero_da_linha:>3} | "
                    f"{registro.codigo_estacao} | nível {registro.alerta_nivel} | "
                    f"{registro.alerta_codigo}"
                )
    else:
        partes.append("  Nenhum alerta registrado no período.")

    partes.append(subtitulo("5. Firmwares em operação (ER-06)"))
    for versao, quantidade in firmwares(resultado).items():
        estaveis = [r for r in resultado.registros if r.firmware == versao and r.estavel]
        marca = "estável" if estaveis else "pré-lançamento"
        partes.append(f"  {versao:<22} {quantidade} registro(s)   [{marca}]")

    avisos = [
        (r.numero_da_linha, aviso) for r in resultado.registros for aviso in r.avisos
    ]
    if avisos:
        partes.append(subtitulo("6. Avisos semânticos (fora do alcance das ER)"))
        for numero, aviso in avisos:
            partes.append(f"  linha {numero:>3}: {aviso}")

    if resultado.invalidas:
        partes.append(subtitulo("7. Registros rejeitados"))
        for invalida in resultado.invalidas:
            partes.append(f"  linha {invalida.numero_da_linha:>3}: {invalida.conteudo}")
            for mensagem in invalida.mensagens:
                partes.append(f"      ↳ {mensagem}")

    if detalhar:
        partes.append(subtitulo("8. Registros válidos (detalhe)"))
        for registro in resultado.registros:
            sub = f".{registro.sub_estacao}" if registro.sub_estacao else ""
            partes.append(
                f"  [{registro.numero_da_linha:>3}] {registro.codigo_estacao}{sub} "
                f"em {registro.instante.isoformat()} "
                f"({registro.latitude}, {registro.longitude})"
            )
            for leitura in registro.leituras:
                partes.append(f"        • {leitura}")

    return "\n".join(partes)


# ---------------------------------------------------------------------------
# Fichas das Expressões Regulares
# ---------------------------------------------------------------------------


def ficha_em_texto(ficha: FichaER, com_automato: bool = False) -> str:
    automato = obter_automato(ficha.identificacao)
    linhas = [
        titulo(f"{ficha.identificacao} — {ficha.nome}"),
        f"Finalidade    : {ficha.finalidade}",
        f"Aplicada em   : {ficha.campo_do_registro}",
        f"Alfabeto (Σ)  : {ficha.alfabeto}",
        f"Linguagem (L) : {ficha.linguagem}",
        "",
        "ER formal     :",
    ]
    for linha in ficha.er_formal.splitlines():
        linhas.append(f"    {linha}")
    linhas += ["", f"Sintaxe no código (Python):", f"    r\"{ficha.sintaxe}\"", ""]
    linhas.append("Equivalência atalho → operador formal:")
    linhas += [f"    {item}" for item in ficha.equivalencia]
    linhas.append("")
    linhas.append("Operadores utilizados:")
    linhas += [f"    - {item}" for item in ficha.operadores]
    linhas.append("")
    linhas.append(
        f"AFNε          : {len(automato.estados)} estados, "
        f"{len(automato.transicoes)} transições, "
        f"{len(automato.movimentos_vazios)} movimentos vazios "
        f"(diagrama em docs/diagramas/{ficha.identificacao}.svg)"
    )
    linhas.append("")
    linhas.append("Cadeias aceitas:")
    linhas += [f"    ✓ {c}" for c in ficha.aceitas]
    linhas.append("Cadeias rejeitadas:")
    linhas += [f"    ✗ {c}" for c in ficha.rejeitadas]
    linhas.append("")
    linhas.append(f"Caso-limite   : {ficha.caso_limite}")
    linhas.append(f"Resultado/limite: {ficha.resultado_e_limite}")
    if com_automato:
        linhas.append("")
        linhas.append(automato.formal())
    return "\n".join(linhas)


def todas_as_fichas(com_automato: bool = False) -> str:
    return "\n".join(ficha_em_texto(f, com_automato) for f in FICHAS)


# ---------------------------------------------------------------------------
# Validação avulsa de cadeia
# ---------------------------------------------------------------------------


def relatorio_de_validacao(ficha: FichaER, cadeia: str, com_trilha: bool = False) -> str:
    automato = obter_automato(ficha.identificacao)
    por_er = ficha.aceita(cadeia)
    por_afne = automato.aceita(cadeia)
    linhas = [
        f"Cadeia analisada : \"{cadeia}\"",
        f"Expressão Regular: {ficha.identificacao} ({ficha.nome})",
        f"  padrão         : r\"{ficha.sintaxe}\"",
        f"  resultado ER   : {'ACEITA' if por_er else 'REJEITADA'}",
        f"  resultado AFNε : {'ACEITA' if por_afne else 'REJEITADA'}",
        f"  equivalência   : {'ok' if por_er == por_afne else 'DIVERGÊNCIA!'}",
    ]
    if com_trilha:
        linhas.append("  trilha de simulação do AFNε:")
        for simbolo, estados in automato.trilha(cadeia):
            ordenados = sorted(estados, key=lambda e: int(e[1:]))
            rotulo = "∅" if not ordenados else "{" + ", ".join(ordenados) + "}"
            linhas.append(f"      {simbolo:<20} → {rotulo}")
    return "\n".join(linhas)
