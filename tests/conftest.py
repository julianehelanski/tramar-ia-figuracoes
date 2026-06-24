"""Configuração de testes: põe `scripts/` no path de importação.

Os scripts do pipeline importam módulos vizinhos (`_paths`, `04_lexical_coding`)
por nome simples, então o diretório precisa estar em `sys.path` durante os testes.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
