"""Etapa 3: gráficos de leitura do contraste técnico contra crítico.

Lê `outputs/etapa3_distribuicao/contraste_polos.csv` (gerado por
`09_contraste_polos.py`) e produz duas figuras de leitura em `outputs/figuras/`:

1. barras agrupadas: cada família com suas barras técnico e crítico lado a lado;
2. barras divergentes: a diferença (técnico menos crítico) por família, ordenada,
   que mostra de imediato para qual polo cada figuração pende.

Uso:
    python scripts/10_graficos_contraste.py
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from _paths import ETAPA3, FIGURAS_DIR

COR_TECNICO = "#1f6f8b"
COR_CRITICO = "#c1432e"


def carregar() -> pd.DataFrame:
    """Lê a tabela de contraste (famílias nas linhas, polos nas colunas)."""
    df = pd.read_csv(ETAPA3 / "contraste_polos.csv", index_col=0)
    df.index.name = "familia"
    return df


def grafico_agrupado(df: pd.DataFrame) -> None:
    """Barras horizontais agrupadas, técnico e crítico por família."""
    ordem = df.max(axis=1).sort_values().index
    d = df.loc[ordem]
    y = range(len(d))
    altura = 0.4
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(
        [i + altura / 2 for i in y],
        d["técnico"],
        altura,
        label="técnico (CS, Engenharia)",
        color=COR_TECNICO,
    )
    ax.barh(
        [i - altura / 2 for i in y],
        d["crítico"],
        altura,
        label="crítico (Humanas, Sociais)",
        color=COR_CRITICO,
    )
    ax.set_yticks(list(y))
    ax.set_yticklabels(d.index)
    ax.set_xlabel("ocorrências por 100 artigos")
    ax.set_title("Famílias figurativas por polo (amostra global de IA)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(FIGURAS_DIR / "contraste_barras_agrupadas.png", dpi=150)
    plt.close(fig)


def grafico_divergente(df: pd.DataFrame) -> None:
    """Barras divergentes: técnico menos crítico, por família, ordenado."""
    dif = (df["técnico"] - df["crítico"]).sort_values()
    cores = [COR_CRITICO if v < 0 else COR_TECNICO for v in dif]
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(dif.index, dif.values, color=cores)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel(
        "← pende ao crítico    |    diferença (técnico − crítico)    |    pende ao técnico →"
    )
    ax.set_title("Para que polo cada figuração pende (ocorrências por 100 artigos)")
    plt.tight_layout()
    plt.savefig(FIGURAS_DIR / "contraste_divergente.png", dpi=150)
    plt.close(fig)


def main() -> None:
    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)
    df = carregar()
    grafico_agrupado(df)
    grafico_divergente(df)
    print("Figuras geradas em", FIGURAS_DIR)
    print(" - contraste_barras_agrupadas.png")
    print(" - contraste_divergente.png")


if __name__ == "__main__":
    main()
