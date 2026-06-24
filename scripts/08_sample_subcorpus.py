"""Etapa 4: seleção do subcorpus para leitura próxima por densidade figurativa.

Operacionaliza a decisão 2.d (`docs/decisoes_metodologicas.md`): amostragem
orientada por informação, no sentido de Flyvbjerg, que privilegia os artigos com
mais figuração medida na Etapa 2, em vez de impacto ou representatividade
estatística. A seleção é estratificada por período e por estrato disciplinar, para
cobrir a variação do campo, e usa `seed=42` no desempate.

Densidade figurativa de um artigo: soma das ocorrências das nove famílias dividida
pelo comprimento do resumo em palavras, para não premiar apenas resumos longos. A
contagem de citações entra como coluna descritiva, sem peso na ordenação.

Marca os selecionados em `no_subcorpus` no metadado e escreve a tabela ordenada do
subcorpus em `outputs/etapa4_leitura/subcorpus.csv`.

Uso:
    python scripts/08_sample_subcorpus.py --alvo 40
    python scripts/08_sample_subcorpus.py --alvo 40 --estrato categoria_wos --bin-anos 3
"""

from __future__ import annotations

import argparse

import pandas as pd

from _paths import ETAPA4, METADATA_CSV, SEED, matriz_lexical_path


def densidade_figurativa(matriz: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
    """Calcula a densidade figurativa por artigo a partir da matriz e do resumo.

    Returns:
        DataFrame com `id`, `ocorrencias` (soma das famílias) e `densidade`
        (ocorrências por palavra do resumo).
    """
    familias = [c for c in matriz.columns if c != "id"]
    base = matriz.copy()
    base["ocorrencias"] = base[familias].sum(axis=1)

    palavras = (
        meta.set_index("id")["abstract"].fillna("").str.split().map(len)
    )
    base = base.merge(palavras.rename("n_palavras"), on="id", how="left")
    base["n_palavras"] = base["n_palavras"].replace(0, pd.NA)
    base["densidade"] = (base["ocorrencias"] / base["n_palavras"]).fillna(0.0)
    return base[["id", "ocorrencias", "densidade"]]


def faixa_periodo(ano: object, bin_anos: int) -> str:
    """Rótulo da faixa de período de um ano, em blocos de `bin_anos`."""
    try:
        a = int(ano)
    except (TypeError, ValueError):
        return "sem_ano"
    inicio = (a // bin_anos) * bin_anos
    return f"{inicio}-{inicio + bin_anos - 1}"


def selecionar(df: pd.DataFrame, alvo: int, estrato: str) -> pd.DataFrame:
    """Seleciona até `alvo` artigos por densidade, repartidos entre os estratos.

    Reparte a cota proporcionalmente ao tamanho de cada estrato e, dentro de cada
    um, escolhe os de maior densidade. Desempate reprodutível por `id` com `SEED`.
    """
    df = df.sample(frac=1, random_state=SEED)  # embaralha para desempate estável
    df = df.sort_values(["densidade"], ascending=False, kind="stable")

    grupos = list(df.groupby(estrato, sort=False))
    n_total = len(df)
    escolhidos = []
    for chave, grupo in grupos:
        cota = max(1, round(alvo * len(grupo) / n_total))
        escolhidos.append(grupo.head(cota))

    sub = pd.concat(escolhidos, ignore_index=True)
    sub = sub.sort_values("densidade", ascending=False, kind="stable")
    return sub.head(alvo)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--alvo", type=int, default=40,
                        help="tamanho do subcorpus (30 a 50 pela decisão 2.d)")
    parser.add_argument("--estrato", default="categoria_wos",
                        help="coluna de estrato disciplinar (padrão: categoria_wos)")
    parser.add_argument("--bin-anos", type=int, default=3,
                        help="tamanho da faixa de período, em anos")
    args = parser.parse_args()

    meta = pd.read_csv(METADATA_CSV)
    if "incluido" in meta.columns:
        meta = meta[meta["incluido"] == True]  # noqa: E712
    matriz = pd.read_csv(matriz_lexical_path())

    dens = densidade_figurativa(matriz, meta)
    df = meta.merge(dens, on="id", how="inner")
    df["faixa_periodo"] = df["ano"].map(lambda a: faixa_periodo(a, args.bin_anos))
    df["estrato_amostral"] = (
        df[args.estrato].fillna("sem_estrato").astype(str) + " | " + df["faixa_periodo"]
    )

    sub = selecionar(df, args.alvo, "estrato_amostral")

    # Marca a seleção no metadado completo (fonte da verdade), sem reescrever filtros.
    meta_full = pd.read_csv(METADATA_CSV)
    meta_full["no_subcorpus"] = meta_full["id"].isin(sub["id"])
    meta_full.to_csv(METADATA_CSV, index=False)

    cols = ["id", "titulo", "ano", "fonte", "estrato_amostral", "ocorrencias",
            "densidade", "citacoes"]
    cols = [c for c in cols if c in sub.columns]
    ETAPA4.mkdir(parents=True, exist_ok=True)
    saida = ETAPA4 / "subcorpus.csv"
    sub[cols].to_csv(saida, index=False)

    print(f"Subcorpus de {len(sub)} artigos (alvo {args.alvo}) em {saida}")
    print(f"Estratos cobertos: {sub['estrato_amostral'].nunique()}")
    print("Citações registradas como descritor, sem peso na seleção (decisão 2.d).")


if __name__ == "__main__":
    main()
