"""Etapa 3: análise textual exploratória, sem o catálogo de famílias.

Análise indutiva dos resumos, que deixa os termos emergirem por si, sem nenhuma
categoria figurativa imposta. Serve de contraponto e de controle de qualidade ao
catálogo: mostra o que de fato distingue o vocabulário de cada polo, antes de
qualquer leitura categórica.

Produz:
1. frequência geral dos termos (após remoção de palavras funcionais en/pt/es);
2. palavras-chave de cada polo por keyness (log-verossimilhança G2, o padrão da
   linguística de corpus): os termos sobre-representados no polo técnico contra o
   crítico;
3. n-gramas (bigramas e trigramas) mais frequentes, no todo e por polo;
4. uma figura com as palavras mais distintivas de cada polo.

Nada aqui usa `campos_lexicais/`. As saídas vão para `outputs/exploratorio/`.

Uso:
    python scripts/13_analise_textual_exploratoria.py
    python scripts/13_analise_textual_exploratoria.py --top 40 --min-df 5
"""

from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from _paths import FIGURAS_DIR, METADATA_CSV, OUTPUTS_DIR
from sklearn.feature_extraction.text import CountVectorizer

POLO = {
    "Computer Science": "técnico",
    "Engineering": "técnico",
    "Arts and Humanities": "crítico",
    "Social Sciences": "crítico",
    "Psychology": "crítico",
}
COR_TECNICO = "#1f6f8b"
COR_CRITICO = "#c1432e"

# Palavras funcionais e de chavão acadêmico (en/pt/es). Não removo vocabulário de
# conteúdo (model, learning, network...), porque é justamente o que interessa ver.
STOPWORDS = set("""
a an and are as at be by for from has have in into is it its of on or that the to with
we our this these those they their which using used use based paper study studies results
result approach approaches method methods model models propose proposed present presents
show shows new also can may such been being more most than then there here was were will
between within during per via given both each other into out over under above below not no
however thus while but about through across among several various many much made make makes
need needs find finds finding findings argue argues draw draws drawing two one three first
second work works abstract article paper papers towards toward including particular often
rather well able whether due upon according address addresses provide provides provided
o a os as de da do das dos e em um uma para por com que se na no como entre sobre este esta
esse essa aos pelo pela ser foi sao são este trabalho artigo nos nas mais muito tambem também
ao à às num numa pelos pelas isso isto ja já
el la los las de del y en un una para por con que se como entre sobre este esta ese esa al
ser fue son este trabajo articulo mas muy tambien lo su sus nos
""".split())


def carregar() -> pd.DataFrame:
    """Resumos incluídos, com polo derivado da categoria disciplinar."""
    df = pd.read_csv(METADATA_CSV)
    if "incluido" in df.columns:
        df = df[df["incluido"] == True]  # noqa: E712
    df = df[df["abstract"].notna() & (df["abstract"].astype(str).str.len() > 0)].copy()
    # Polo por fonte (coluna `polo`) quando existe; senão, por área (`categoria_wos`).
    if "polo" in df.columns and df["polo"].notna().any():
        df["polo"] = df["polo"].fillna("outro")
    else:
        df["polo"] = df["categoria_wos"].map(POLO).fillna("outro")
    return df


def frequencia(textos: list[str], min_df: int) -> pd.DataFrame:
    """Frequência total de cada termo unigrama."""
    vec = CountVectorizer(
        stop_words=list(STOPWORDS), min_df=min_df, token_pattern=r"(?u)\b[^\W\d_][^\W\d_]+\b"
    )
    x = vec.fit_transform(textos)
    freq = np.asarray(x.sum(axis=0)).ravel()
    return (
        pd.DataFrame({"termo": vec.get_feature_names_out(), "frequencia": freq})
        .sort_values("frequencia", ascending=False)
        .reset_index(drop=True)
    )


def keyness(df: pd.DataFrame, min_df: int) -> pd.DataFrame:
    """Keyness por log-verossimilhança (G2) entre polo técnico e crítico.

    Para cada termo: G2 mede o quanto sua frequência se afasta do esperado se os dois
    polos fossem iguais. O sinal indica o polo onde o termo é sobre-representado.
    """
    sub = df[df["polo"].isin(["técnico", "crítico"])]
    vec = CountVectorizer(
        stop_words=list(STOPWORDS), min_df=min_df, token_pattern=r"(?u)\b[^\W\d_][^\W\d_]+\b"
    )
    x = vec.fit_transform(sub["abstract"].astype(str))
    termos = vec.get_feature_names_out()

    eh_tec = (sub["polo"] == "técnico").to_numpy()
    a = np.asarray(x[eh_tec].sum(axis=0)).ravel().astype(float)  # técnico
    b = np.asarray(x[~eh_tec].sum(axis=0)).ravel().astype(float)  # crítico
    c, d = a.sum(), b.sum()

    e1 = c * (a + b) / (c + d)
    e2 = d * (a + b) / (c + d)
    with np.errstate(divide="ignore", invalid="ignore"):
        t1 = np.where(a > 0, a * np.log(a / e1), 0.0)
        t2 = np.where(b > 0, b * np.log(b / e2), 0.0)
    g2 = 2 * (t1 + t2)
    sinal = np.sign(a / c - b / d)

    return (
        pd.DataFrame(
            {
                "termo": termos,
                "freq_tecnico": a.astype(int),
                "freq_critico": b.astype(int),
                "por_mil_tecnico": (a / c * 1000).round(3),
                "por_mil_critico": (b / d * 1000).round(3),
                "keyness_g2": g2.round(2),
                "polo": np.where(sinal >= 0, "técnico", "crítico"),
            }
        )
        .sort_values("keyness_g2", ascending=False)
        .reset_index(drop=True)
    )


def ngramas(textos: list[str], min_df: int, n: int = 30) -> pd.DataFrame:
    """Bigramas e trigramas mais frequentes."""
    vec = CountVectorizer(
        stop_words=list(STOPWORDS),
        ngram_range=(2, 3),
        min_df=min_df,
        token_pattern=r"(?u)\b[^\W\d_][^\W\d_]+\b",
    )
    x = vec.fit_transform(textos)
    freq = np.asarray(x.sum(axis=0)).ravel()
    return (
        pd.DataFrame({"ngrama": vec.get_feature_names_out(), "frequencia": freq})
        .sort_values("frequencia", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )


def figura_keyness(key: pd.DataFrame, saida, top: int = 20) -> None:
    """Barras das palavras mais distintivas de cada polo, lado a lado."""
    tec = key[key["polo"] == "técnico"].head(top).iloc[::-1]
    cri = key[key["polo"] == "crítico"].head(top).iloc[::-1]
    fig, eixos = plt.subplots(1, 2, figsize=(14, 8))
    eixos[0].barh(cri["termo"], cri["keyness_g2"], color=COR_CRITICO)
    eixos[0].set_title("distintivas do polo crítico")
    eixos[1].barh(tec["termo"], tec["keyness_g2"], color=COR_TECNICO)
    eixos[1].set_title("distintivas do polo técnico")
    for ax in eixos:
        ax.set_xlabel("keyness (G2)")
    fig.suptitle("Palavras-chave por polo, sem categorias (análise indutiva)", fontsize=13)
    plt.tight_layout()
    plt.savefig(saida, dpi=150)
    plt.close(fig)


def figura_barras(
    df: pd.DataFrame,
    coluna_termo: str,
    coluna_valor: str,
    titulo: str,
    xlabel: str,
    saida,
    top: int = 25,
) -> None:
    """Barras horizontais de uma tabela termo/valor (frequência ou n-gramas)."""
    d = df.head(top).iloc[::-1]
    plt.figure(figsize=(9, max(5, top * 0.32)))
    plt.barh(d[coluna_termo], d[coluna_valor], color="#3a6f5c")
    plt.xlabel(xlabel)
    plt.title(titulo)
    plt.tight_layout()
    plt.savefig(saida, dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top", type=int, default=40, help="quantos termos por saída")
    parser.add_argument("--min-df", type=int, default=5, help="frequência mínima de documento")
    args = parser.parse_args()

    df = carregar()
    saida_dir = OUTPUTS_DIR / "exploratorio"
    saida_dir.mkdir(parents=True, exist_ok=True)
    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)

    freq = frequencia(df["abstract"].astype(str).tolist(), args.min_df)
    freq.head(args.top).to_csv(saida_dir / "frequencia_geral.csv", index=False)

    key = keyness(df, args.min_df)
    key.to_csv(saida_dir / "keyness_por_polo.csv", index=False)

    ng = ngramas(df["abstract"].astype(str).tolist(), args.min_df, args.top)
    ng.to_csv(saida_dir / "ngramas.csv", index=False)

    figura_keyness(key, FIGURAS_DIR / "keyness_polos.png", min(20, args.top))
    figura_barras(
        freq,
        "termo",
        "frequencia",
        "Termos mais frequentes no corpus",
        "frequência",
        FIGURAS_DIR / "frequencia_geral.png",
        min(25, args.top),
    )
    figura_barras(
        ng,
        "ngrama",
        "frequencia",
        "N-gramas mais frequentes no corpus",
        "frequência",
        FIGURAS_DIR / "ngramas.png",
        min(25, args.top),
    )

    print(f"Resumos analisados: {len(df)}  (sem usar o catálogo de famílias)")
    print(f"\nTop 15 termos gerais:\n{freq.head(15).to_string(index=False)}")
    print(
        f"\nMais distintivos do polo TÉCNICO:\n"
        f"{key[key['polo'] == 'técnico'].head(15)[['termo', 'keyness_g2', 'por_mil_tecnico']].to_string(index=False)}"
    )
    print(
        f"\nMais distintivos do polo CRÍTICO:\n"
        f"{key[key['polo'] == 'crítico'].head(15)[['termo', 'keyness_g2', 'por_mil_critico']].to_string(index=False)}"
    )
    print(f"\nSaídas em {saida_dir} e figura em {FIGURAS_DIR / 'keyness_polos.png'}")


if __name__ == "__main__":
    main()
