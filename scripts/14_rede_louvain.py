"""Etapa 3: rede de co-ocorrência de termos com comunidades de Louvain.

Análise indutiva de rede textual, sem o catálogo de famílias. Constrói a rede em que
os nós são os termos mais frequentes dos resumos e as arestas ligam termos que
coaparecem no mesmo resumo, com peso igual ao número de resumos em que coaparecem.
Sobre essa rede, aplica a detecção de comunidades de Louvain (modularidade), que
agrupa os termos em clusters temáticos emergentes do próprio corpus.

É o equivalente, em script, da leitura de rede textual que o roteiro prevê (Gephi,
InfraNodus): mostra os discursos do corpus como vizinhanças de palavras, sem categoria
imposta. Seed fixo (`SEED`) para reprodutibilidade do particionamento e do layout.

Saídas: `outputs/figuras/rede_louvain.png` e
`outputs/exploratorio/comunidades_louvain.csv` (termo, comunidade, frequência).

Uso:
    python scripts/14_rede_louvain.py
    python scripts/14_rede_louvain.py --top-termos 120 --min-assoc 0.25
"""

from __future__ import annotations

import argparse

import community as community_louvain
import matplotlib

matplotlib.use("Agg")
# Reaproveita a lista de stopwords da análise exploratória.
import importlib.util
from pathlib import Path

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from _paths import FIGURAS_DIR, METADATA_CSV, OUTPUTS_DIR, SEED
from sklearn.feature_extraction.text import CountVectorizer

_spec = importlib.util.spec_from_file_location(
    "_expl", Path(__file__).resolve().parent / "13_analise_textual_exploratoria.py"
)
_expl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_expl)
STOPWORDS = _expl.STOPWORDS


def carregar_textos() -> list[str]:
    """Resumos não vazios dos artigos incluídos."""
    df = pd.read_csv(METADATA_CSV)
    if "incluido" in df.columns:
        df = df[df["incluido"] == True]  # noqa: E712
    abst = df["abstract"].dropna().astype(str)
    return abst[abst.str.len() > 0].tolist()


def cooccorrencia(textos: list[str], top: int, min_df: int):
    """Matriz de co-ocorrência dos `top` termos mais frequentes e suas frequências."""
    vec = CountVectorizer(
        stop_words=list(STOPWORDS),
        max_features=top,
        min_df=min_df,
        binary=True,
        token_pattern=r"(?u)\b[^\W\d_][^\W\d_]+\b",
    )
    x = vec.fit_transform(textos)
    termos = vec.get_feature_names_out()
    freq = np.asarray(x.sum(axis=0)).ravel()
    co = (x.T @ x).toarray()
    np.fill_diagonal(co, 0)
    return termos, freq, co


def construir_grafo(termos, freq, co, min_assoc: float) -> nx.Graph:
    """Grafo por força de associação (cosseno) entre termos.

    A aresta usa a associação normalizada `co_ij / sqrt(freq_i * freq_j)`, que tira o
    efeito da frequência bruta. Num corpus grande, o limiar absoluto de co-ocorrência
    geraria um grafo quase completo; a associação dá uma rede com estrutura de
    comunidades. Mantém arestas acima de `min_assoc`.
    """
    g = nx.Graph()
    g.add_nodes_from(termos)
    n = len(termos)
    for i in range(n):
        for j in range(i + 1, n):
            denom = (freq[i] * freq[j]) ** 0.5
            assoc = co[i, j] / denom if denom else 0.0
            if assoc >= min_assoc:
                g.add_edge(termos[i], termos[j], weight=float(assoc))
    g.remove_nodes_from(list(nx.isolates(g)))
    return g


def desenhar(g: nx.Graph, particao: dict, freq_map: dict, saida) -> None:
    """Desenha a rede colorida por comunidade, nós dimensionados pela frequência."""
    pos = nx.spring_layout(g, weight="weight", seed=SEED, k=0.5)
    comunidades = sorted(set(particao.values()))
    cores = cm.tab10(np.linspace(0, 1, max(10, len(comunidades))))
    cor_no = [cores[particao[n] % len(cores)] for n in g.nodes()]
    fmax = max(freq_map.values()) or 1
    tam = [120 + 1400 * freq_map.get(n, 0) / fmax for n in g.nodes()]

    plt.figure(figsize=(15, 11))
    nx.draw_networkx_edges(g, pos, alpha=0.15, edge_color="#999999")
    nx.draw_networkx_nodes(g, pos, node_color=cor_no, node_size=tam, alpha=0.85)
    nx.draw_networkx_labels(g, pos, font_size=8)
    plt.title(
        f"Rede de co-ocorrência de termos, comunidades de Louvain "
        f"({len(comunidades)} comunidades)"
    )
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(saida, dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top-termos", type=int, default=120, help="quantos termos na rede")
    parser.add_argument(
        "--min-assoc",
        type=float,
        default=0.25,
        help="força de associação mínima da aresta (cosseno, 0 a 1)",
    )
    parser.add_argument("--min-df", type=int, default=5, help="frequência mínima de documento")
    args = parser.parse_args()

    textos = carregar_textos()
    termos, freq, co = cooccorrencia(textos, args.top_termos, args.min_df)
    freq_map = dict(zip(termos, freq, strict=True))

    g = construir_grafo(termos, freq, co, args.min_assoc)
    if g.number_of_edges() == 0:
        raise SystemExit("Rede vazia; baixe --min-assoc ou suba --top-termos.")

    particao = community_louvain.best_partition(g, weight="weight", random_state=SEED)
    mod = community_louvain.modularity(particao, g, weight="weight")

    saida_dir = OUTPUTS_DIR / "exploratorio"
    saida_dir.mkdir(parents=True, exist_ok=True)
    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)

    tabela = pd.DataFrame(
        {
            "termo": list(g.nodes()),
            "comunidade": [particao[n] for n in g.nodes()],
            "frequencia": [int(freq_map.get(n, 0)) for n in g.nodes()],
        }
    ).sort_values(["comunidade", "frequencia"], ascending=[True, False])
    tabela.to_csv(saida_dir / "comunidades_louvain.csv", index=False)

    desenhar(g, particao, freq_map, FIGURAS_DIR / "rede_louvain.png")

    print(f"Rede: {g.number_of_nodes()} termos, {g.number_of_edges()} arestas")
    print(f"Comunidades de Louvain: {len(set(particao.values()))} (modularidade {mod:.3f})")
    for com in sorted(set(particao.values())):
        termos_com = tabela[tabela["comunidade"] == com]["termo"].head(10).tolist()
        print(f"  comunidade {com}: {', '.join(termos_com)}")
    print(f"\nFigura em {FIGURAS_DIR / 'rede_louvain.png'}; tabela em {saida_dir}")


if __name__ == "__main__":
    main()
