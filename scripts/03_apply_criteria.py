"""Etapa 1: aplica critérios de inclusão e exclusão e gera contagem PRISMA.

Marca cada registro do corpus como incluído ou excluído conforme os critérios da
seção 4.1 do roteiro (tipo de documento, idioma, período, presença de análise
textual) e preenche `motivo_exclusao`. Imprime a contagem para o fluxograma
PRISMA.

Os critérios automatizáveis (período, idioma, tipo de documento) rodam aqui; os
de juízo (análise textual presente, reflexão epistêmica) ficam para triagem
manual sobre o subconjunto que passa nos automáticos.

Uso:
    python scripts/03_apply_criteria.py
"""

from __future__ import annotations

import pandas as pd

from _paths import METADATA_CSV

ANO_MIN, ANO_MAX = 2015, 2026
IDIOMAS = {"en", "pt", "es"}
# Decisão 2.a (docs/decisoes_metodologicas.md): incluir "Proceedings Paper" ou não.
TIPOS_INCLUIDOS = {"Article", "Review", "Proceedings Paper"}


def aplicar_criterios(df: pd.DataFrame) -> pd.DataFrame:
    """Marca inclusão/exclusão pelos critérios automatizáveis."""
    df = df.copy()
    df["incluido"] = True
    df["motivo_exclusao"] = ""

    def excluir(mask: pd.Series, motivo: str) -> None:
        alvo = mask & df["incluido"]
        df.loc[alvo, "incluido"] = False
        df.loc[alvo, "motivo_exclusao"] = motivo

    excluir(~df["ano"].between(ANO_MIN, ANO_MAX), "fora do periodo")
    excluir(~df["idioma"].isin(IDIOMAS), "idioma fora do escopo")
    excluir(~df["tipo_doc"].isin(TIPOS_INCLUIDOS), "tipo de documento excluido")
    return df


def main() -> None:
    df = pd.read_csv(METADATA_CSV)
    df = aplicar_criterios(df)
    df.to_csv(METADATA_CSV, index=False)

    incluidos = int(df["incluido"].sum())
    print(f"Incluídos pelos critérios automáticos: {incluidos} de {len(df)}")
    print(df.loc[~df["incluido"], "motivo_exclusao"].value_counts().to_string())
    print("\nTriagem manual pendente: análise textual presente, reflexão epistêmica.")
    print("Registrar contagem em docs/prisma/fluxograma_prisma.md")


if __name__ == "__main__":
    main()
