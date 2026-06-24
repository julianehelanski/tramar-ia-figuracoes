"""Etapa 2, nível 1: codificação lexical por família semântica.

Conta ocorrências de cada família do catálogo (`campos_lexicais/
catalogo_familias.yaml`) sobre o texto disponível de cada artigo (resumo, ou
texto integral quando presente em `fulltext_dir()`). Produz a matriz artigo ×
família, em versão bruta. Para as famílias marcadas com `desambiguar: true`
(antropomorfica, militar), a versão refinada é aplicada por
`04b_desambiguar.py` a partir do CSV manual, nunca recomputada aqui.

Correspondência case-insensitive com fronteira de palavra; espaços no termo
viram `\\s+`.

Uso:
    python scripts/04_lexical_coding.py
"""

from __future__ import annotations

import re

import pandas as pd
import yaml

from _paths import CATALOGO_PATH, ETAPA2, METADATA_CSV


def carregar_catalogo() -> dict:
    """Carrega o catálogo de famílias do YAML."""
    with open(CATALOGO_PATH, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def compilar_padroes(termos: list[str]) -> re.Pattern:
    """Compila um padrão único (alternância) com fronteira de palavra."""
    partes = [re.escape(t).replace(r"\ ", r"\s+") for t in termos]
    return re.compile(r"\b(?:" + "|".join(partes) + r")\b", re.IGNORECASE)


def contar(texto: str, padrao: re.Pattern) -> int:
    """Conta ocorrências de um padrão num texto."""
    return len(padrao.findall(str(texto)))


def codificar(df: pd.DataFrame, catalogo: dict) -> pd.DataFrame:
    """Gera a matriz artigo × família (contagem bruta sobre o resumo)."""
    padroes = {
        fam: compilar_padroes(meta["termos"]) for fam, meta in catalogo.items()
    }
    linhas = []
    for _, art in df.iterrows():
        texto = art.get("abstract", "")
        linha = {"id": art["id"]}
        linha.update({fam: contar(texto, p) for fam, p in padroes.items()})
        linhas.append(linha)
    return pd.DataFrame(linhas)


def main() -> None:
    df = pd.read_csv(METADATA_CSV)
    df = df[df["incluido"]] if "incluido" in df.columns else df
    catalogo = carregar_catalogo()
    matriz = codificar(df, catalogo)

    ETAPA2.mkdir(parents=True, exist_ok=True)
    saida = ETAPA2 / "codificacao_lexical.csv"
    matriz.to_csv(saida, index=False)
    print(f"Matriz {matriz.shape[0]} artigos × {matriz.shape[1] - 1} famílias em {saida}")
    print("Famílias com desambiguação pendente: antropomorfica, militar (ver decisão 3).")


if __name__ == "__main__":
    main()
