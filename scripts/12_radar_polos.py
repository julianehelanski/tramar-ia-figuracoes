"""Etapa 3: radar de perfil figurativo dos dois polos.

Lê `contraste_polos.csv` e desenha um gráfico de radar (teia) com as nove famílias
nos eixos e dois polígonos sobrepostos, técnico e crítico, em ocorrências por 100
artigos. O radar mostra o perfil figurativo de cada polo de relance: onde cada um se
estende e onde se recolhe.

Uso:
    python scripts/12_radar_polos.py
"""

from __future__ import annotations

import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from _paths import ETAPA3, FIGURAS_DIR

COR_TECNICO = "#1f6f8b"
COR_CRITICO = "#c1432e"


def main() -> None:
    df = pd.read_csv(ETAPA3 / "contraste_polos.csv", index_col=0)
    familias = list(df.index)
    n = len(familias)
    angulos = [i / n * 2 * math.pi for i in range(n)]
    angulos += angulos[:1]  # fecha o polígono

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"polar": True})
    for polo, cor in [("técnico", COR_TECNICO), ("crítico", COR_CRITICO)]:
        valores = df[polo].tolist()
        valores += valores[:1]
        ax.plot(angulos, valores, color=cor, linewidth=2, label=polo)
        ax.fill(angulos, valores, color=cor, alpha=0.18)

    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(familias, fontsize=10)
    ax.set_title("Perfil figurativo por polo (ocorrências por 100 artigos)", pad=24)
    ax.legend(loc="upper right", bbox_to_anchor=(1.15, 1.1))
    plt.tight_layout()

    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)
    saida = FIGURAS_DIR / "radar_polos.png"
    plt.savefig(saida, dpi=150)
    print(f"Figura em {saida}")


if __name__ == "__main__":
    main()
