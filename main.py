#!/usr/bin/env python3
"""
MeteoRegex — ponto de entrada da aplicação.

Uso rápido:
    python main.py                                  # menu interativo
    python main.py -a dados/telemetria_setembro.log # analisa um arquivo
    python main.py -l "PA-BEL-004A|...|fw-v3.11.2"  # analisa uma linha
    python main.py -e ER-03 -c "TEMP=+27.4C"        # testa uma cadeia
    python main.py -f                               # fichas das ER
    python main.py -t                               # bateria de casos de teste
"""

import sys

from analisador.cli import principal

if __name__ == "__main__":
    sys.exit(principal())
