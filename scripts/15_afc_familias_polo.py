"""Etapa 3: análise fatorial de correspondência (AFC) famílias × estrato.

Posiciona as nove famílias figurativas e os estratos do corpus num mesmo plano
fatorial, pela análise de correspondência (a AFC da escola francesa, a mesma do
IRaMuTeQ). A AFC decompõe a tabela de contingência famílias × estrato em eixos de
inércia: famílias próximas de um estrato no mapa têm perfil de ocorrência associado
a ele, e a distância à origem mede o quanto a família se afasta do perfil médio.

Por que estrato e não só polo: uma AFC de famílias contra dois polos colapsa numa
única dimensão (o número de eixos é `min(linhas-1, colunas-1)`, que com duas colunas
é um). Para um mapa de duas dimensões, a coluna é o estrato: cada periódico do polo
crítico entra como coluna própria e o polo técnico se desdobra por campo disciplinar
(`categoria_wos`). Cada estrato pertence a um único polo, então o mapa se deixa
colorir por polo, e a oposição técnico contra crítico aparece como eixo emergente.

A decomposição é por SVD (determinística, sem semente), sobre os resíduos
padronizados da tabela de contingência. Sem dependência nova: numpy basta.

Saídas:
    outputs/etapa3_distribuicao/afc_coordenadas_familias.csv
    outputs/etapa3_distribuicao/afc_coordenadas_estratos.csv
    outputs/etapa3_distribuicao/afc_inercia.csv
    outputs/figuras/afc_familias_estrato.png
    outputs/latex/afc_coordenadas_familias.tex

Uso:
    python scripts/15_afc_familias_polo.py
    python scripts/15_afc_familias_polo.py --coluna estrato --min-estrato 30
    python scripts/15_afc_familias_polo.py --coluna polo   # versão 1D (famílias × polo)
"""

from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from _paths import ETAPA3, FIGURAS_DIR, LATEX_DIR, METADATA_CSV, matriz_lexical_path

# Mapa de campo disciplinar (categoria_wos) para polo, recuo quando não há coluna `polo`.
POLO = {
    "Computer Science": "técnico",
    "Engineering": "técnico",
    "Arts and Humanities": "crítico",
    "Social Sciences": "crítico",
    "Psychology": "crítico",
}
COR_POLO = {"técnico": "#1f6f8b", "crítico": "#c1432e", "outro": "#888888"}
COR_FAMILIA = "#222222"


def carregar() -> tuple[pd.DataFrame, list[str]]:
    """Junta a matriz lexical (refinada quando existe) aos metadados de estrato."""
    matriz = pd.read_csv(matriz_lexical_path())
    meta = pd.read_csv(METADATA_CSV)
    familias = [c for c in matriz.columns if c != "id"]
    cols = ["id", "categoria_wos", "fonte"] + (["polo"] if "polo" in meta.columns else [])
    df = matriz.merge(meta[cols], on="id", how="left")
    if "polo" in df.columns and df["polo"].notna().any():
        df["polo"] = df["polo"].fillna("outro")
    else:
        df["polo"] = df["categoria_wos"].map(POLO).fillna("outro")
    return df, familias


def coluna_estrato(df: pd.DataFrame, modo: str) -> pd.Series:
    """Define a variável de coluna da tabela de contingência.

    `estrato`: periódico (fonte) nos artigos críticos, campo disciplinar precedido de
    \"técnico:\" nos técnicos; mantém cada comunidade crítica separada e agrupa o polo
    técnico por campo. `fonte`, `categoria_wos` e `polo` usam a coluna homônima direta.
    """
    if modo == "estrato":
        critico = df["fonte"].fillna("").astype(str).str.strip()
        tecnico = "técnico: " + df["categoria_wos"].fillna("").astype(str).str.strip()
        return np.where(df["polo"] == "crítico", critico, tecnico)
    if modo in {"fonte", "categoria_wos", "polo"}:
        return df[modo].fillna("").astype(str).str.strip()
    raise ValueError(f"modo de coluna desconhecido: {modo}")


def tabela_contingencia(
    df: pd.DataFrame, familias: list[str], min_estrato: int
) -> tuple[pd.DataFrame, dict[str, str]]:
    """Contingência famílias (linhas) × estrato (colunas), com mapa estrato→polo.

    Cada célula soma as ocorrências da família nos artigos do estrato. Descarta
    estratos com menos de `min_estrato` artigos ou sem nenhuma ocorrência.
    """
    n_art = df.groupby("estrato").size()
    estratos_ok = n_art[n_art >= min_estrato].index
    df = df[df["estrato"].isin(estratos_ok)]

    soma = df.groupby("estrato")[familias].sum()
    soma = soma.loc[:, soma.sum(axis=0) > 0]  # famílias sem ocorrência saem
    soma = soma[soma.sum(axis=1) > 0]  # estratos sem ocorrência saem
    tabela = soma.T  # famílias nas linhas, estratos nas colunas

    polo_de = df.groupby("estrato")["polo"].agg(lambda s: s.value_counts().idxmax()).to_dict()
    return tabela, polo_de


def afc(tabela: pd.DataFrame) -> dict:
    """Análise de correspondência por SVD dos resíduos padronizados.

    Devolve coordenadas principais de linhas e colunas, inércias por eixo e a fração
    de inércia explicada. A formulação `Dr^-1/2 (P - r c^T) Dc^-1/2` já remove o eixo
    trivial, então todos os eixos retornados são não triviais.
    """
    n = tabela.to_numpy(dtype=float)
    total = n.sum()
    p = n / total
    r = p.sum(axis=1)  # massas de linha
    c = p.sum(axis=0)  # massas de coluna
    dr_isqrt = 1.0 / np.sqrt(r)
    dc_isqrt = 1.0 / np.sqrt(c)

    s = (p - np.outer(r, c)) * dr_isqrt[:, None] * dc_isqrt[None, :]
    u, sigma, vt = np.linalg.svd(s, full_matrices=False)

    inercia = sigma**2
    explica = inercia / inercia.sum()
    coord_linha = dr_isqrt[:, None] * u * sigma[None, :]
    coord_coluna = dc_isqrt[:, None] * vt.T * sigma[None, :]
    return {
        "linhas": coord_linha,
        "colunas": coord_coluna,
        "inercia": inercia,
        "explica": explica,
        "massa_linha": r,
        "massa_coluna": c,
        "nomes_linha": list(tabela.index),
        "nomes_coluna": list(tabela.columns),
    }


def desenhar(res: dict, polo_de: dict[str, str], saida) -> None:
    """Biplot da AFC: famílias rotuladas e estratos coloridos por polo."""
    fl, fc = res["linhas"], res["colunas"]
    ex = res["explica"]
    eixo_y = 1 if fl.shape[1] > 1 else 0

    plt.figure(figsize=(12, 9))
    plt.axhline(0, color="#cccccc", lw=0.8, zorder=0)
    plt.axvline(0, color="#cccccc", lw=0.8, zorder=0)

    # Estratos (colunas), por polo.
    for j, nome in enumerate(res["nomes_coluna"]):
        polo = polo_de.get(nome, "outro")
        plt.scatter(fc[j, 0], fc[j, eixo_y], marker="s", s=70, color=COR_POLO[polo], zorder=3)
        plt.annotate(
            nome,
            (fc[j, 0], fc[j, eixo_y]),
            fontsize=8,
            color=COR_POLO[polo],
            xytext=(4, 4),
            textcoords="offset points",
        )

    # Famílias (linhas).
    for i, nome in enumerate(res["nomes_linha"]):
        plt.scatter(fl[i, 0], fl[i, eixo_y], marker="o", s=90, color=COR_FAMILIA, zorder=4)
        plt.annotate(
            nome,
            (fl[i, 0], fl[i, eixo_y]),
            fontsize=10,
            fontweight="bold",
            color=COR_FAMILIA,
            xytext=(4, -10),
            textcoords="offset points",
        )

    plt.xlabel(f"eixo 1 ({ex[0] * 100:.1f}% da inércia)")
    rotulo_y = f"eixo 2 ({ex[eixo_y] * 100:.1f}% da inércia)" if eixo_y else "eixo 2 (degenerado)"
    plt.ylabel(rotulo_y)
    plt.title("AFC: famílias figurativas e estratos do corpus (técnico contra crítico)")
    handles = [
        plt.Line2D([], [], marker="s", ls="", color=COR_POLO["crítico"], label="estrato crítico"),
        plt.Line2D([], [], marker="s", ls="", color=COR_POLO["técnico"], label="estrato técnico"),
        plt.Line2D([], [], marker="o", ls="", color=COR_FAMILIA, label="família figurativa"),
    ]
    plt.legend(handles=handles, loc="best", fontsize=9)
    plt.tight_layout()
    plt.savefig(saida, dpi=150)
    plt.close()


def salvar_tabelas(res: dict, polo_de: dict[str, str]) -> None:
    """Grava coordenadas, inércias e a versão LaTeX das coordenadas das famílias."""
    ETAPA3.mkdir(parents=True, exist_ok=True)
    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)
    LATEX_DIR.mkdir(parents=True, exist_ok=True)

    k = res["linhas"].shape[1]
    eixos = [f"eixo_{d + 1}" for d in range(k)]

    fam = pd.DataFrame(res["linhas"], columns=eixos)
    fam.insert(0, "familia", res["nomes_linha"])
    fam.insert(1, "massa", res["massa_linha"].round(4))
    fam.to_csv(ETAPA3 / "afc_coordenadas_familias.csv", index=False)

    est = pd.DataFrame(res["colunas"], columns=eixos)
    est.insert(0, "estrato", res["nomes_coluna"])
    est.insert(1, "polo", [polo_de.get(nm, "outro") for nm in res["nomes_coluna"]])
    est.insert(2, "massa", res["massa_coluna"].round(4))
    est.to_csv(ETAPA3 / "afc_coordenadas_estratos.csv", index=False)

    inr = pd.DataFrame(
        {
            "eixo": eixos,
            "inercia": res["inercia"].round(5),
            "inercia_pct": (res["explica"] * 100).round(2),
            "inercia_acum_pct": (np.cumsum(res["explica"]) * 100).round(2),
        }
    )
    inr.to_csv(ETAPA3 / "afc_inercia.csv", index=False)

    cols_latex = ["familia", "massa"] + eixos[: min(2, k)]
    latex = fam[cols_latex].to_latex(
        index=False,
        float_format="%.3f",
        caption=(
            "Coordenadas das famílias figurativas nos dois primeiros eixos da AFC "
            "(famílias por estrato), corpus por periódico."
        ),
        label="tab:afc_familias",
    )
    (LATEX_DIR / "afc_coordenadas_familias.tex").write_text(latex, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--coluna",
        choices=["estrato", "fonte", "categoria_wos", "polo"],
        default="estrato",
        help="variável de coluna da tabela de contingência (padrão: estrato)",
    )
    parser.add_argument(
        "--min-estrato",
        type=int,
        default=30,
        help="descarta estratos com menos artigos que este limiar",
    )
    args = parser.parse_args()

    df, familias = carregar()
    df["estrato"] = coluna_estrato(df, args.coluna)
    tabela, polo_de = tabela_contingencia(df, familias, args.min_estrato)

    if tabela.shape[1] < 2:
        raise SystemExit(
            f"Só {tabela.shape[1]} estrato(s) após o corte; baixe --min-estrato ou "
            "troque --coluna para um nível com mais categorias."
        )

    res = afc(tabela)
    salvar_tabelas(res, polo_de)
    desenhar(res, polo_de, FIGURAS_DIR / "afc_familias_estrato.png")

    print(f"Tabela de contingência: {tabela.shape[0]} famílias × {tabela.shape[1]} estratos")
    print("\nInércia por eixo:")
    for d, frac in enumerate(res["explica"][: min(5, len(res["explica"]))]):
        print(
            f"  eixo {d + 1}: {frac * 100:5.1f}%  (acumulado {np.cumsum(res['explica'])[d] * 100:5.1f}%)"
        )
    print("\nFamílias no plano (eixo 1, eixo 2):")
    k = res["linhas"].shape[1]
    for i, nome in enumerate(res["nomes_linha"]):
        y = res["linhas"][i, 1] if k > 1 else 0.0
        print(f"  {nome:16s} ({res['linhas'][i, 0]:+.3f}, {y:+.3f})")
    print("\nEstratos no plano (eixo 1, eixo 2), por polo:")
    for j, nome in enumerate(res["nomes_coluna"]):
        y = res["colunas"][j, 1] if k > 1 else 0.0
        print(
            f"  [{polo_de.get(nome, 'outro'):7s}] {nome[:34]:34s} ({res['colunas'][j, 0]:+.3f}, {y:+.3f})"
        )
    print(f"\nFigura em {FIGURAS_DIR / 'afc_familias_estrato.png'}")
    print(f"Coordenadas e inércia em {ETAPA3}")


if __name__ == "__main__":
    main()
