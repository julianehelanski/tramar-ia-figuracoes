"""Etapa 3 (opcional): topic modeling sobre o corpus.

Aplica LDA (gensim) ou BERTopic ao corpus de resumos para identificar tópicos
latentes e cruzá-los com a categorização figurativa. Seed fixo (SEED) para
reprodutibilidade. BERTopic é dependência opcional (extra `topic`).

Uso:
    python scripts/07_topic_model.py --metodo lda --n-topicos 15
"""

from __future__ import annotations

import argparse

import pandas as pd

from _paths import ETAPA3, METADATA_CSV, SEED


def rodar_lda(textos: list[str], n_topicos: int) -> None:
    """Treina LDA com gensim e salva os tópicos. Seed fixo via random_state=SEED."""
    # TODO: tokenização (spaCy en/pt/es), dicionário e corpus gensim, LdaModel
    # com random_state=SEED. Salvar tópicos em ETAPA3 / "topicos_lda.csv".
    raise NotImplementedError(
        "Implementar após a codificação lexical estabilizar; cruzar tópicos com "
        "as nove famílias do catálogo."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metodo", choices=["lda", "bertopic"], default="lda")
    parser.add_argument("--n-topicos", type=int, default=15)
    args = parser.parse_args()

    meta = pd.read_csv(METADATA_CSV)
    textos = meta.loc[meta.get("incluido", True), "abstract"].fillna("").tolist()
    ETAPA3.mkdir(parents=True, exist_ok=True)
    print(f"Seed fixo: {SEED}. Método: {args.metodo}. Tópicos: {args.n_topicos}.")

    if args.metodo == "lda":
        rodar_lda(textos, args.n_topicos)
    else:
        raise NotImplementedError("BERTopic: instalar extra `topic` e implementar.")


if __name__ == "__main__":
    main()
