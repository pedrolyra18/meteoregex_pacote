#!/usr/bin/env python3
"""
Gerador da documentação das Expressões Regulares
================================================

Produz `docs/expressoes_regulares.md` e `docs/afne_formal.md` a partir das
fichas declaradas em `analisador.expressoes` e dos autômatos de
`analisador.automatos`. Como tudo é extraído do código, a documentação nunca
fica defasada em relação ao programa.

Uso:
    python ferramentas/gerar_documentacao.py
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from analisador.automatos import AUTOMATOS, DESCRICAO_CLASSES, EPSILON  # noqa: E402
from analisador.expressoes import FICHAS  # noqa: E402

CABECALHO = """# Expressões Regulares do MeteoRegex

> Documento **gerado automaticamente** por `ferramentas/gerar_documentacao.py`
> a partir do código-fonte (`analisador/expressoes.py` e
> `analisador/automatos.py`). Qualquer alteração no programa se reflete aqui,
> o que garante a exigência do enunciado: *a expressão formal, a expressão da
> apresentação, o padrão implementado, os testes e o AFNε representam a mesma
> linguagem*.

Motor de Expressões Regulares: módulo `re` da biblioteca padrão do Python 3.
Toda validação usa `re.fullmatch`, isto é, a **cadeia inteira** precisa
pertencer à linguagem — nenhum casamento parcial é aceito.

Recursos deliberadamente **não utilizados** (seção 4 do guia de sintaxe):
retroreferências, recursão, condicionais e lookaround. Todos os agrupamentos
são não capturantes `(?:r)`, equivalentes ao agrupamento formal `( r )`.

| ER | Nome | Campo do registro | Estados do AFNε | Movimentos ε |
|----|------|-------------------|-----------------|--------------|
"""


def _tabela_resumo() -> str:
    linhas = []
    for ficha in FICHAS:
        automato = AUTOMATOS[ficha.identificacao]
        linhas.append(
            f"| {ficha.identificacao} | {ficha.nome} | {ficha.campo_do_registro} | "
            f"{len(automato.estados)} | {len(automato.movimentos_vazios)} |"
        )
    return "\n".join(linhas)


def _ficha_markdown(ficha) -> str:
    automato = AUTOMATOS[ficha.identificacao]
    partes = [f"\n---\n\n## {ficha.identificacao} — {ficha.nome}\n"]
    partes.append(f"**Finalidade no programa.** {ficha.finalidade}\n")
    partes.append(f"**Onde é aplicada.** {ficha.campo_do_registro}\n")
    partes.append("### Alfabeto (Σ)\n")
    partes.append(f"```\n{ficha.alfabeto}\n```\n")
    partes.append("### Linguagem reconhecida (L)\n")
    partes.append(f"{ficha.linguagem}\n")
    partes.append("### Expressão Regular na notação formal\n")
    partes.append(f"```\n{ficha.er_formal}\n```\n")
    partes.append("### Sintaxe exatamente como aparece no código-fonte\n")
    partes.append(f'```python\nr"{ficha.sintaxe}"\n```\n')
    partes.append("### Equivalência entre os atalhos e os operadores formais\n")
    for item in ficha.equivalencia:
        partes.append(f"- `{item}`")
    partes.append("\n### Explicação dos operadores utilizados\n")
    for item in ficha.operadores:
        partes.append(f"- {item}")
    partes.append(f"\n### AFNε correspondente\n")
    partes.append(
        f"![AFNε {ficha.identificacao}](diagramas/{ficha.identificacao}.svg)\n"
    )
    partes.append(
        f"- estado inicial: `{automato.inicial}`\n"
        f"- estados finais: {', '.join('`' + e + '`' for e in sorted(automato.finais))}\n"
        f"- total de estados: {len(automato.estados)}\n"
        f"- total de transições: {len(automato.transicoes)}\n"
        f"- movimentos vazios (ε): {len(automato.movimentos_vazios)}\n"
    )
    partes.append(
        "A descrição formal completa (Q, Σ, δ, q₀, F) está em "
        "[`afne_formal.md`](afne_formal.md) e pode ser exibida pelo programa "
        f"com `python main.py -f -e {ficha.identificacao} --afne`.\n"
    )
    partes.append("### Testes\n")
    partes.append("| # | Cadeia aceita | Cadeia rejeitada |")
    partes.append("|---|---------------|------------------|")
    for indice in range(max(len(ficha.aceitas), len(ficha.rejeitadas))):
        aceita = f"`{ficha.aceitas[indice]}`" if indice < len(ficha.aceitas) else ""
        rejeitada = (
            f"`{ficha.rejeitadas[indice]}`" if indice < len(ficha.rejeitadas) else ""
        )
        partes.append(f"| {indice + 1} | {aceita} | {rejeitada} |")
    partes.append(f"\n**Caso-limite.** {ficha.caso_limite}\n")
    partes.append(f"**Resultado observado e limitações.** {ficha.resultado_e_limite}\n")
    return "\n".join(partes)


def gerar_expressoes(destino: Path) -> Path:
    conteudo = [CABECALHO + _tabela_resumo() + "\n"]
    for ficha in FICHAS:
        conteudo.append(_ficha_markdown(ficha))
    arquivo = destino / "expressoes_regulares.md"
    arquivo.write_text("\n".join(conteudo), encoding="utf-8")
    return arquivo


def gerar_afne(destino: Path) -> Path:
    partes = [
        "# Descrição formal dos AFNε\n",
        "> Documento gerado automaticamente por "
        "`ferramentas/gerar_documentacao.py`.\n",
        "Cada autômato é uma quíntupla **A = (Q, Σ, δ, q₀, F)**. As transições "
        "são apresentadas na forma `δ(estado, símbolo) ∋ estado`, pois em um "
        "AFNε a função de transição devolve um *conjunto* de estados.\n",
        "Classes de símbolos usadas nos rótulos (abreviações da união dos "
        "símbolos correspondentes):\n",
    ]
    for descricao in DESCRICAO_CLASSES.values():
        partes.append(f"- `{descricao}`")
    partes.append(
        f"\nO símbolo `{EPSILON}` indica movimento vazio: muda de estado sem "
        "consumir símbolo algum da entrada.\n"
    )
    for identificador, automato in AUTOMATOS.items():
        partes.append(f"\n---\n\n## {identificador}\n")
        partes.append(f"```\n{automato.formal()}\n```\n")
    arquivo = destino / "afne_formal.md"
    arquivo.write_text("\n".join(partes), encoding="utf-8")
    return arquivo


if __name__ == "__main__":
    pasta = RAIZ / "docs"
    pasta.mkdir(exist_ok=True)
    for gerado in (gerar_expressoes(pasta), gerar_afne(pasta)):
        print(f"gerado: {gerado.relative_to(RAIZ)}")
