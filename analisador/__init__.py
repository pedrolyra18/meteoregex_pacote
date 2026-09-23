"""
MeteoRegex — analisador de telemetria de estações meteorológicas.

Trabalho do 1o bimestre da disciplina de Linguagens Formais e Autômatos.

Módulos:
    expressoes  — as seis Expressões Regulares e suas fichas de documentação;
    automatos   — os AFNε equivalentes, com construtor e simulador;
    processador — leitura, validação e extração dos registros de telemetria;
    relatorio   — formatação das saídas;
    cli         — interface de linha de comando e menu interativo.
"""

__version__ = "1.0.0"
__all__ = ["expressoes", "automatos", "processador", "relatorio", "cli"]
