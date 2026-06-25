"""Etapa 3: redes de co-ocorrência das famílias figurativas, por polo.

Para cada polo (técnico e crítico), constrói a rede em que os nós são as nove
famílias e as arestas ligam famílias que coaparecem no mesmo artigo, com peso igual
ao número de artigos em que coaparecem. Desenha as duas redes lado a lado, com o
mesmo arranjo de nós, para comparar como a figuração se agrupa em cada polo.

O tamanho do nó reflete a prevalência da família no polo (quantos artigos a usam); a
espessura da aresta reflege a co-ocorrência; a cor do nó indica para que polo a
família pende no contraste (`contraste_polos.csv`), quando disponível.

Lê a matriz refinada quando existe (senão a bruta) e os metadados (`categoria_wos`).

Uso:
    python scripts/11_redes_polos.py
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from _paths import ETAPA3, FIGURAS_DIR, METADATA_CSV, matriz_lexical_path

POLO = {
    "Computer Science": "técnico",
    "Engineering": "técnico",
    "Arts and Humanities": "crítico",
    "Social Sciences": "crítico",
    "Psychology": "crítico",
}
COR_TECNICO = "#1f6f8b"
COR_CRITICO = "#c1432e"


def cooccorrencia(binaria: pd.DataFrame) -> pd.DataFrame:
    """Matriz família × família de co-ocorrência (artigos em que ambas aparecem)."""
    return binaria.T.dot(binaria)


def cor_dos_nos(familias: list[str]) -> dict[str, str]:
    """Cor de cada família pelo polo a que pende no contraste, se houver a tabela."""
    caminho = ETAPA3 / "contraste_polos.csv"
    if not caminho.exists():
        return {f: "#888888" for f in familias}
    c = pd.read_csv(caminho, index_col=0)
    lean = c["técnico"] - c["crítico"]
    return {f: (COR_TECNICO if lean.get(f, 0) >= 0 else COR_CRITICO) for f in familias}


def desenhar(
    ax, co: pd.DataFrame, familias: list[str], pos, cores: dict[str, str], titulo: str
) -> None:
    """Desenha uma rede de co-ocorrência num eixo."""
    g = nx.Graph()
    for f in familias:
        g.add_node(f, tam=int(co.loc[f, f]))
    for i, a in enumerate(familias):
        for b in familias[i + 1 :]:
            peso = int(co.loc[a, b])
            if peso > 0:
                g.add_edge(a, b, weight=peso)

    tam_max = max((co.loc[f, f] for f in familias), default=1) or 1
    tamanhos = [300 + 2200 * co.loc[f, f] / tam_max for f in familias]
    peso_max = max((d["weight"] for *_, d in g.edges(data=True)), default=1) or 1
    larguras = [0.4 + 5 * d["weight"] / peso_max for *_, d in g.edges(data=True)]

    nx.draw_networkx_edges(g, pos, ax=ax, width=larguras, edge_color="#bbbbbb")
    nx.draw_networkx_nodes(
        g,
        pos,
        ax=ax,
        nodelist=familias,
        node_size=tamanhos,
        node_color=[cores[f] for f in familias],
        alpha=0.85,
    )
    nx.draw_networkx_labels(g, pos, ax=ax, font_size=9)
    ax.set_title(titulo)
    ax.axis("off")


def main() -> None:
    matriz = pd.read_csv(matriz_lexical_path())
    meta = pd.read_csv(METADATA_CSV)
    familias = [c for c in matriz.columns if c != "id"]

    cols = ["id", "categoria_wos"] + (["polo"] if "polo" in meta.columns else [])
    df = matriz.merge(meta[cols], on="id", how="left")
    if "polo" in df.columns and df["polo"].notna().any():
        df["polo"] = df["polo"].fillna("outro")
    else:
        df["polo"] = df["categoria_wos"].map(POLO).fillna("outro")

    pos = nx.circular_layout(familias)
    cores = cor_dos_nos(familias)

    fig, eixos = plt.subplots(1, 2, figsize=(15, 7))
    for ax, polo in zip(eixos, ["técnico", "crítico"], strict=True):
        sub = df[df["polo"] == polo]
        binaria = (sub[familias] > 0).astype(int)
        co = cooccorrencia(binaria)
        desenhar(ax, co, familias, pos, cores, f"polo {polo} (n={len(sub)})")

    fig.suptitle("Redes de co-ocorrência das famílias figurativas, por polo", fontsize=13)
    plt.tight_layout()
    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)
    saida = FIGURAS_DIR / "redes_polos.png"
    plt.savefig(saida, dpi=150)
    print(f"Figura em {saida}")


if __name__ == "__main__":
    main()
