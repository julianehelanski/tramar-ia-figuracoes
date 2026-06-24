"""Etapa 3: distribuição das famílias por subcampo disciplinar e por período.

Cruza a matriz de codificação lexical com os metadados (categoria WoS, ano) para
ver a distribuição relativa das famílias por estrato disciplinar e ao longo do
tempo. Gera tabelas em `outputs/etapa3_distribuicao/` e figuras em
`outputs/figuras/`.

Uso:
    python scripts/06_distribution.py
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from _paths import ETAPA2, ETAPA3, FIGURAS_DIR, METADATA_CSV


def juntar(matriz: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
    """Junta a matriz lexical aos metadados por `id`."""
    cols = ["id", "ano", "categoria_wos", "idioma"]
    return matriz.merge(meta[cols], on="id", how="left")


def por_periodo(df: pd.DataFrame, familias: list[str]) -> pd.DataFrame:
    """Soma de ocorrências por família e ano, normalizada por artigos no ano."""
    return df.groupby("ano")[familias].sum()


def por_disciplina(df: pd.DataFrame, familias: list[str]) -> pd.DataFrame:
    """Soma de ocorrências por família e categoria WoS."""
    return df.groupby("categoria_wos")[familias].sum()


def main() -> None:
    matriz = pd.read_csv(ETAPA2 / "codificacao_lexical.csv")
    meta = pd.read_csv(METADATA_CSV)
    familias = [c for c in matriz.columns if c != "id"]

    df = juntar(matriz, meta)
    ETAPA3.mkdir(parents=True, exist_ok=True)
    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)

    tempo = por_periodo(df, familias)
    tempo.to_csv(ETAPA3 / "distribuicao_temporal.csv")
    disc = por_disciplina(df, familias)
    disc.to_csv(ETAPA3 / "distribuicao_disciplinar.csv")

    ax = tempo.plot(figsize=(10, 6))
    ax.set_xlabel("ano")
    ax.set_ylabel("ocorrências")
    ax.set_title("Famílias figurativas por período")
    plt.tight_layout()
    plt.savefig(FIGURAS_DIR / "distribuicao_temporal.png", dpi=150)
    print(f"Tabelas em {ETAPA3}; figura em {FIGURAS_DIR}")


if __name__ == "__main__":
    main()
