"""Etapa 3: contraste figurativo entre o polo técnico e o polo crítico.

Cruza a matriz de codificação lexical com o estrato disciplinar de cada artigo
(`categoria_wos`, que para a importação OpenAlex traz o *field* do tópico primário)
e agrupa os campos em dois polos:
    técnico  = Computer Science, Engineering
    crítico  = Arts and Humanities, Social Sciences

Reporta as ocorrências por família a cada 100 artigos em cada polo, para controlar o
tamanho diferente de cada estrato, e salva uma figura de contraste. Usa a matriz
refinada por desambiguação quando ela existe; caso contrário, a bruta (e então as
famílias biológica e antropomórfica vêm infladas pela homonímia técnica).

Uso:
    python scripts/09_contraste_polos.py
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from _paths import ETAPA3, FIGURAS_DIR, METADATA_CSV, matriz_lexical_path

# Mapa de field (categoria_wos) para polo.
POLO = {
    "Computer Science": "técnico",
    "Engineering": "técnico",
    "Arts and Humanities": "crítico",
    "Social Sciences": "crítico",
    "Psychology": "crítico",
}


def main() -> None:
    matriz = pd.read_csv(matriz_lexical_path())
    meta = pd.read_csv(METADATA_CSV)
    familias = [c for c in matriz.columns if c != "id"]

    # Polo por fonte (coluna `polo`, recorte por periódico) quando existe; senão, por
    # área disciplinar (`categoria_wos`).
    cols = ["id", "categoria_wos"] + (["polo"] if "polo" in meta.columns else [])
    df = matriz.merge(meta[cols], on="id", how="left")
    if "polo" in df.columns and df["polo"].notna().any():
        df["polo"] = df["polo"].fillna("outro")
    else:
        df["polo"] = df["categoria_wos"].map(POLO).fillna("outro")
    df = df[df["polo"].isin(["técnico", "crítico"])]

    n_por_polo = df["polo"].value_counts()
    soma = df.groupby("polo")[familias].sum()
    por_100 = soma.div(n_por_polo, axis=0).mul(100).round(2)

    print("Artigos por polo:")
    print(n_por_polo.to_string())
    print("\nOcorrências por família a cada 100 artigos, por polo:")
    print(por_100.T.to_string())  # famílias nas linhas, polos nas colunas

    ETAPA3.mkdir(parents=True, exist_ok=True)
    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)
    por_100.T.to_csv(ETAPA3 / "contraste_polos.csv")

    plt.figure(figsize=(7, 5))
    sns.heatmap(
        por_100.T,
        annot=True,
        fmt=".1f",
        cmap="rocket_r",
        cbar_kws={"label": "ocorrências por 100 artigos"},
    )
    plt.title("Figurações por polo: técnico contra crítico (IA, amostra global)")
    plt.xlabel("polo")
    plt.ylabel("família figurativa")
    plt.tight_layout()
    plt.savefig(FIGURAS_DIR / "contraste_polos.png", dpi=150)
    print(f"\nTabela em {ETAPA3 / 'contraste_polos.csv'}")
    print(f"Figura em {FIGURAS_DIR / 'contraste_polos.png'}")


if __name__ == "__main__":
    main()
