"""Caminhos centralizados do projeto.

Importado pelos scripts do pipeline para resolver diretórios de saída por etapa
sem hardcoding em cada script, em coerência com a organização de `outputs/`.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[1]

CORPUS_DIR = REPO_ROOT / "corpus"
QUERIES_DIR = CORPUS_DIR / "queries"
METADATA_DIR = CORPUS_DIR / "metadata"
CATALOGO_PATH = REPO_ROOT / "campos_lexicais" / "catalogo_familias.yaml"

OUTPUTS_DIR = REPO_ROOT / "outputs"
ETAPA1 = OUTPUTS_DIR / "etapa1_corpus"
ETAPA2 = OUTPUTS_DIR / "etapa2_codificacao"
ETAPA3 = OUTPUTS_DIR / "etapa3_distribuicao"
ETAPA4 = OUTPUTS_DIR / "etapa4_leitura"
FIGURAS_DIR = OUTPUTS_DIR / "figuras"
LATEX_DIR = OUTPUTS_DIR / "latex"

SEED = 42

METADATA_CSV = METADATA_DIR / "corpus_metadata.csv"


def exports_dir() -> Path:
    """Diretório das exportações brutas das bases.

    Usa CORPUS_EXPORTS_PATH do `.env` se definido; senão, corpus/exports/.
    """
    externo = os.getenv("CORPUS_EXPORTS_PATH")
    if externo:
        return Path(externo)
    return CORPUS_DIR / "exports"


def fulltext_dir() -> Path | None:
    """Diretório do texto integral dos artigos (copyright, fora do repositório).

    Retorna None se CORPUS_FULLTEXT_PATH não estiver definido no `.env`.
    """
    caminho = os.getenv("CORPUS_FULLTEXT_PATH")
    return Path(caminho) if caminho else None
