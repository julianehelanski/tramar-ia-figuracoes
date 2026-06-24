"""Etapa 3: matriz de co-ocorrência de famílias e exportação para rede.

Sobre a matriz de codificação lexical, constrói a co-ocorrência entre famílias
(artigos em que duas famílias aparecem juntas) e exporta um grafo para
visualização em Gephi ou InfraNodus.

Uso:
    python scripts/05_cooccurrence.py
"""

from __future__ import annotations

import networkx as nx
import pandas as pd

from _paths import ETAPA2, ETAPA3


def matriz_cooccorrencia(matriz: pd.DataFrame) -> pd.DataFrame:
    """Co-ocorrência de famílias: presença binária por artigo, produto cruzado."""
    familias = [c for c in matriz.columns if c != "id"]
    binaria = (matriz[familias] > 0).astype(int)
    co = binaria.T.dot(binaria)
    return co


def construir_grafo(co: pd.DataFrame) -> nx.Graph:
    """Grafo não-direcionado ponderado de co-ocorrência entre famílias."""
    g = nx.Graph()
    familias = list(co.columns)
    for fam in familias:
        g.add_node(fam, ocorrencias=int(co.loc[fam, fam]))
    for i, a in enumerate(familias):
        for b in familias[i + 1 :]:
            peso = int(co.loc[a, b])
            if peso > 0:
                g.add_edge(a, b, weight=peso)
    return g


def main() -> None:
    matriz = pd.read_csv(ETAPA2 / "codificacao_lexical.csv")
    co = matriz_cooccorrencia(matriz)
    ETAPA3.mkdir(parents=True, exist_ok=True)
    co.to_csv(ETAPA3 / "cooccorrencia_familias.csv")

    g = construir_grafo(co)
    nx.write_graphml(g, ETAPA3 / "rede_familias.graphml")
    print(f"Co-ocorrência salva; rede com {g.number_of_nodes()} nós e "
          f"{g.number_of_edges()} arestas em {ETAPA3 / 'rede_familias.graphml'}")


if __name__ == "__main__":
    main()
