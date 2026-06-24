"""Etapa 1: deduplica o corpus por DOI e título normalizado.

Lê `corpus/metadata/corpus_metadata.csv`, remove duplicatas (chave primária DOI;
fallback por título normalizado quando o DOI falta) e registra a contagem de
removidos para o fluxograma PRISMA.

Uso:
    python scripts/02_dedup.py
"""

from __future__ import annotations

import re

import pandas as pd

from _paths import METADATA_CSV


def normalizar_titulo(titulo: str) -> str:
    """Normaliza título para deduplicação: minúsculas, sem pontuação nem espaços."""
    return re.sub(r"[^a-z0-9]", "", str(titulo).lower())


def deduplicar(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Remove duplicatas por DOI e, na ausência dele, por título normalizado.

    Returns:
        (corpus deduplicado, número de registros removidos).
    """
    n0 = len(df)
    com_doi = df[df["doi"].notna() & (df["doi"].astype(str).str.len() > 0)]
    sem_doi = df[~df.index.isin(com_doi.index)].copy()

    com_doi = com_doi.drop_duplicates(subset="doi", keep="first")
    sem_doi["_titulo_norm"] = sem_doi["titulo"].map(normalizar_titulo)
    sem_doi = sem_doi.drop_duplicates(subset="_titulo_norm", keep="first").drop(
        columns="_titulo_norm"
    )

    dedup = pd.concat([com_doi, sem_doi], ignore_index=True)
    return dedup, n0 - len(dedup)


def main() -> None:
    df = pd.read_csv(METADATA_CSV)
    dedup, removidos = deduplicar(df)
    dedup.to_csv(METADATA_CSV, index=False)
    print(f"{removidos} duplicatas removidas; {len(dedup)} registros restantes.")
    print("Registrar a contagem em docs/prisma/fluxograma_prisma.md")


if __name__ == "__main__":
    main()
