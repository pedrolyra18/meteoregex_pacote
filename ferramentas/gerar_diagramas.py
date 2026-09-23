#!/usr/bin/env python3
"""
Gerador dos diagramas dos AFNε
==============================

Lê os autômatos definidos em `analisador.automatos` e produz um arquivo SVG
por autômato em `docs/diagramas/`. Como os diagramas são gerados a partir da
mesma estrutura que o programa simula, eles não podem divergir do código.

Uso:
    python ferramentas/gerar_diagramas.py
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from analisador.automatos import AUTOMATOS, CLASSES, EPSILON, AFNe  # noqa: E402

COLUNAS = 10
LARGURA_COLUNA = 112
ALTURA_LINHA = 150
ALTURA_FAIXA = 76
ESPACO_ENTRE_LINHAS = 70
RAIO = 17
MARGEM_X = 95
MARGEM_Y = 105

COR_FUNDO = "#ffffff"
COR_ESTADO = "#ffffff"
COR_BORDA = "#1f3a5f"
COR_TEXTO = "#0f1c2e"
COR_ARESTA = "#44607f"
COR_EPSILON = "#b3561d"
COR_FINAL = "#e8f1e4"


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------


def _arestas_de_retorno(automato: AFNe) -> set[int]:
    """Marca, por busca em profundidade, as arestas que fecham ciclos."""
    adjacencia: dict[str, list[tuple[int, str]]] = {e: [] for e in automato.estados}
    for indice, (origem, _, destino) in enumerate(automato.transicoes):
        adjacencia[origem].append((indice, destino))

    retorno: set[int] = set()
    cor: dict[str, int] = {e: 0 for e in automato.estados}

    def visitar(estado: str) -> None:
        cor[estado] = 1
        for indice, destino in adjacencia[estado]:
            if cor[destino] == 1:
                retorno.add(indice)
            elif cor[destino] == 0:
                visitar(destino)
        cor[estado] = 2

    visitar(automato.inicial)
    for estado in automato.estados:
        if cor[estado] == 0:
            visitar(estado)
    return retorno


def _camadas(automato: AFNe, retorno: set[int]) -> dict[str, int]:
    """Caminho mais longo a partir do inicial, ignorando arestas de retorno."""
    camada = {estado: 0 for estado in automato.estados}
    for _ in range(len(automato.estados)):
        mudou = False
        for indice, (origem, _, destino) in enumerate(automato.transicoes):
            if indice in retorno:
                continue
            if camada[destino] < camada[origem] + 1:
                camada[destino] = camada[origem] + 1
                mudou = True
        if not mudou:
            break
    return camada


def _posicoes(automato: AFNe) -> tuple[dict[str, tuple[float, float]], int, int]:
    retorno = _arestas_de_retorno(automato)
    camada = _camadas(automato, retorno)
    por_camada: dict[int, list[str]] = {}
    for estado in automato.estados:
        por_camada.setdefault(camada[estado], []).append(estado)

    # altura de cada linha do diagrama: depende de quantos estados dividem a
    # mesma camada (ramos de uma união, por exemplo)
    linhas = {numero // COLUNAS for numero in por_camada}
    faixas_por_linha = {
        linha: max(
            len(estados)
            for numero, estados in por_camada.items()
            if numero // COLUNAS == linha
        )
        for linha in linhas
    }
    base_y: dict[int, float] = {}
    acumulado = float(MARGEM_Y)
    for linha in range(max(linhas) + 1):
        base_y[linha] = acumulado
        acumulado += faixas_por_linha.get(linha, 1) * ALTURA_FAIXA + ESPACO_ENTRE_LINHAS

    posicao: dict[str, tuple[float, float]] = {}
    for numero, estados in por_camada.items():
        coluna = numero % COLUNAS
        linha = numero // COLUNAS
        if linha % 2 == 1:                      # disposição em serpentina
            coluna = COLUNAS - 1 - coluna
        for indice, estado in enumerate(estados):
            x = MARGEM_X + coluna * LARGURA_COLUNA
            y = base_y[linha] + indice * ALTURA_FAIXA
            posicao[estado] = (x, y)

    largura = MARGEM_X * 2 + (COLUNAS - 1) * LARGURA_COLUNA
    altura = acumulado - ESPACO_ENTRE_LINHAS + 40
    return posicao, int(largura), int(altura)


# ---------------------------------------------------------------------------
# Desenho
# ---------------------------------------------------------------------------


def _rotulo_visivel(rotulo: str) -> str:
    return rotulo


def _aresta(x1, y1, x2, y2, rotulo, curvatura):
    """Devolve o caminho SVG e a posição do rótulo."""
    dx, dy = x2 - x1, y2 - y1
    distancia = max((dx * dx + dy * dy) ** 0.5, 1e-6)
    # recua o início e o fim para a borda dos círculos
    ux, uy = dx / distancia, dy / distancia
    if curvatura == 0:
        ax, ay = x1 + ux * RAIO, y1 + uy * RAIO
        bx, by = x2 - ux * (RAIO + 6), y2 - uy * (RAIO + 6)
        caminho = f"M {ax:.1f},{ay:.1f} L {bx:.1f},{by:.1f}"
        return caminho, ((ax + bx) / 2, (ay + by) / 2 - 9)
    # controle deslocado perpendicularmente
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    px, py = -uy, ux
    cx, cy = mx + px * curvatura, my + py * curvatura
    dax, day = cx - x1, cy - y1
    da = max((dax * dax + day * day) ** 0.5, 1e-6)
    ax, ay = x1 + dax / da * RAIO, y1 + day / da * RAIO
    dbx, dby = cx - x2, cy - y2
    db = max((dbx * dbx + dby * dby) ** 0.5, 1e-6)
    bx, by = x2 + dbx / db * (RAIO + 6), y2 + dby / db * (RAIO + 6)
    caminho = f"M {ax:.1f},{ay:.1f} Q {cx:.1f},{cy:.1f} {bx:.1f},{by:.1f}"
    rx = 0.25 * ax + 0.5 * cx + 0.25 * bx
    ry = 0.25 * ay + 0.5 * cy + 0.25 * by
    deslocamento = 15 if curvatura > 0 else -8
    return caminho, (rx, ry + deslocamento)


def desenhar(automato: AFNe) -> str:
    posicao, largura, altura = _posicoes(automato)
    partes: list[str] = []
    partes.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" '
        f'height="{altura}" viewBox="0 0 {largura} {altura}" '
        f'font-family="DejaVu Sans, Verdana, sans-serif">'
    )
    partes.append(
        '<defs><marker id="seta" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{COR_ARESTA}"/></marker>'
        '<marker id="setaeps" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{COR_EPSILON}"/></marker></defs>'
    )
    partes.append(f'<rect width="{largura}" height="{altura}" fill="{COR_FUNDO}"/>')

    # cabeçalho
    partes.append(
        f'<text x="18" y="30" font-size="17" font-weight="bold" fill="{COR_TEXTO}">'
        f'AFNε {automato.identificacao} — {automato.nome}</text>'
    )
    classes_usadas = [r for r in automato.rotulos if r in CLASSES]
    legenda = "  •  ".join(
        f"{c} = [{'A-Z' if c == '⟨M⟩' else '0-9' if c == '⟨D⟩' else '+-' if c == '⟨S⟩' else '1-3'}]"
        for c in classes_usadas
    )
    rodape = (
        f"q{automato.inicial[1:]} inicial (→)  •  estado final em círculo duplo  •  "
        f"{len(automato.estados)} estados, {len(automato.transicoes)} transições, "
        f"{len(automato.movimentos_vazios)} movimentos ε"
    )
    partes.append(
        f'<text x="18" y="50" font-size="12" fill="{COR_ARESTA}">{legenda}</text>'
    )
    partes.append(
        f'<text x="18" y="68" font-size="12" fill="{COR_ARESTA}">{rodape}</text>'
    )

    # arestas
    pares = {(o, d) for o, _, d in automato.transicoes}
    ocupacao: dict[tuple[str, str], int] = {}
    for origem, rotulo, destino in automato.transicoes:
        x1, y1 = posicao[origem]
        x2, y2 = posicao[destino]
        chave = (origem, destino)
        repeticao = ocupacao.get(chave, 0)
        ocupacao[chave] = repeticao + 1

        if origem == destino:
            curvatura = 0.0
            caminho = (
                f"M {x1 - 8:.1f},{y1 - RAIO:.1f} "
                f"C {x1 - 40:.1f},{y1 - 62:.1f} {x1 + 40:.1f},{y1 - 62:.1f} "
                f"{x1 + 8:.1f},{y1 - RAIO:.1f}"
            )
            ponto = (x1, y1 - 50)
        else:
            mesma_faixa = abs(y1 - y2) < 1
            adjacente = abs(abs(x2 - x1) - LARGURA_COLUNA) < 1
            if (destino, origem) in pares:
                # há aresta nos dois sentidos: arqueia as duas para lados opostos
                curvatura = 30.0 + 16 * repeticao
            elif mesma_faixa and adjacente and repeticao == 0:
                curvatura = 0.0
            elif mesma_faixa and not adjacente:
                curvatura = -34.0 - 16 * repeticao
            else:
                curvatura = 26.0 + 16 * repeticao
            caminho, ponto = _aresta(x1, y1, x2, y2, rotulo, curvatura)

        vazio = rotulo == EPSILON
        cor = COR_EPSILON if vazio else COR_ARESTA
        marcador = "setaeps" if vazio else "seta"
        tracejado = ' stroke-dasharray="5 3"' if vazio else ""
        partes.append(
            f'<path d="{caminho}" fill="none" stroke="{cor}" stroke-width="1.5"'
            f'{tracejado} marker-end="url(#{marcador})"/>'
        )
        texto = _escapar(_rotulo_visivel(rotulo))
        partes.append(
            f'<text x="{ponto[0]:.1f}" y="{ponto[1]:.1f}" font-size="13" '
            f'text-anchor="middle" fill="none" stroke="{COR_FUNDO}" '
            f'stroke-width="4" stroke-linejoin="round">{texto}</text>'
        )
        partes.append(
            f'<text x="{ponto[0]:.1f}" y="{ponto[1]:.1f}" font-size="13" '
            f'text-anchor="middle" fill="{cor}">{texto}</text>'
        )

    # estados
    for estado, (x, y) in posicao.items():
        final = estado in automato.finais
        if final:
            partes.append(
                f'<circle cx="{x}" cy="{y}" r="{RAIO + 4}" fill="none" '
                f'stroke="{COR_BORDA}" stroke-width="1.6"/>'
            )
        partes.append(
            f'<circle cx="{x}" cy="{y}" r="{RAIO}" fill="'
            f'{COR_FINAL if final else COR_ESTADO}" stroke="{COR_BORDA}" '
            f'stroke-width="1.6"/>'
        )
        partes.append(
            f'<text x="{x}" y="{y + 4}" font-size="12" text-anchor="middle" '
            f'fill="{COR_TEXTO}">{estado}</text>'
        )

    # seta do estado inicial
    xi, yi = posicao[automato.inicial]
    partes.append(
        f'<path d="M {xi - 52},{yi} L {xi - RAIO - 7},{yi}" stroke="{COR_BORDA}" '
        f'stroke-width="1.8" fill="none" marker-end="url(#seta)"/>'
    )
    partes.append(
        f'<text x="{xi - 52}" y="{yi - 10}" font-size="12" text-anchor="start" '
        f'fill="{COR_BORDA}">início</text>'
    )

    partes.append("</svg>")
    return "\n".join(partes)


def _escapar(texto: str) -> str:
    return (
        texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def gerar_todos(destino: Path | None = None) -> list[Path]:
    destino = destino or (RAIZ / "docs" / "diagramas")
    destino.mkdir(parents=True, exist_ok=True)
    gerados = []
    for identificador, automato in AUTOMATOS.items():
        arquivo = destino / f"{identificador}.svg"
        arquivo.write_text(desenhar(automato), encoding="utf-8")
        gerados.append(arquivo)
        print(f"gerado: {arquivo.relative_to(RAIZ)}  "
              f"({len(automato.estados)} estados, "
              f"{len(automato.movimentos_vazios)} movimentos ε)")
    return gerados


if __name__ == "__main__":
    gerar_todos()
