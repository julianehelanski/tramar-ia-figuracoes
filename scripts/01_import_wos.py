"""Etapa 1: importa exportações de bases bibliográficas e consolida metadados.

Lê exportações brutas (WoS *tab-delimited*, Scopus RIS/CSV) de `exports_dir()` e
escreve um CSV consolidado em `corpus/metadata/corpus_metadata.csv`, no esquema
descrito em `corpus/README.md`.

Uso:
    python scripts/01_import_wos.py --fonte corpus/exports/wos_2026-06.txt --base wos
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from _paths import METADATA_CSV


def importar(fonte: Path, base: str) -> pd.DataFrame:
    """Lê uma exportação e a normaliza para o esquema do corpus.

    Args:
        fonte: caminho do arquivo exportado.
        base: identificador da base de origem (wos, scopus, arxiv).

    Returns:
        DataFrame no esquema de `corpus_metadata.csv`.
    """
    # TODO: ramificar parsing por base (WoS tab-delimited, Scopus RIS via rispy).
    # Por ora, esqueleto: ler e mapear colunas para o esquema mínimo.
    raise NotImplementedError(
        "Implementar parsing por base após a busca-piloto definir o formato de "
        "exportação. Ver corpus/README.md para o esquema-alvo."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fonte", type=Path, required=True, help="arquivo exportado")
    parser.add_argument("--base", required=True, choices=["wos", "scopus", "arxiv"])
    args = parser.parse_args()

    df = importar(args.fonte, args.base)
    METADATA_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(METADATA_CSV, index=False)
    print(f"{len(df)} registros consolidados em {METADATA_CSV}")


if __name__ == "__main__":
    main()
