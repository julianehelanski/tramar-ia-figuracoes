"""Etapa 3 (opcional): topic modeling sobre o corpus.

Aplica LDA (gensim) ou BERTopic ao corpus de resumos para identificar tópicos
latentes e cruzá-los com a categorização figurativa. Seed fixo (SEED) para
reprodutibilidade. BERTopic é dependência opcional (extra `topic`).

Uso:
    python scripts/07_topic_model.py --metodo lda --n-topicos 15
"""

from __future__ import annotations

import argparse
import re

import pandas as pd

from _paths import ETAPA3, METADATA_CSV, SEED

# Stopwords mínimas (en/pt/es) para o caminho LDA leve, sem dependência de spaCy.
# A lematização por spaCy entra como refinamento posterior (ver requirements.txt).
_STOPWORDS = set("""
a an and are as at be by for from has have in into is it its of on or that the to
with we our this these those they their which using used use based paper study
results approach method methods model models propose proposed present show
o a os as de da do das dos e em um uma para por com que se na no como entre sobre
este esta esse essa aos das nas nos ser foi este trabalho artigo
el la los las de del y en un una para por con que se como este esta
""".split())


def tokenizar(texto: str) -> list[str]:
    """Tokeniza em minúsculas, descartando stopwords e tokens curtos/numéricos."""
    tokens = re.findall(r"[a-zA-Záàâãéêíóôõúç]{3,}", str(texto).lower())
    return [t for t in tokens if t not in _STOPWORDS]


def rodar_lda(textos: list[str], n_topicos: int) -> pd.DataFrame:
    """Treina LDA com gensim e devolve os termos por tópico.

    Seed fixo via `random_state=SEED` para reprodutibilidade. Salva os tópicos em
    `ETAPA3 / topicos_lda.csv`. gensim é dependência declarada em requirements.txt.
    """
    try:
        from gensim import corpora
        from gensim.models import LdaModel
    except ImportError as erro:
        raise SystemExit(
            "LDA exige gensim (pip install gensim)."
        ) from erro

    docs = [tokenizar(t) for t in textos]
    docs = [d for d in docs if d]
    if not docs:
        raise SystemExit("Sem texto tokenizável; verifique a coluna abstract.")

    dicionario = corpora.Dictionary(docs)
    dicionario.filter_extremes(no_below=2, no_above=0.5)
    corpus = [dicionario.doc2bow(d) for d in docs]

    lda = LdaModel(corpus=corpus, id2word=dicionario, num_topics=n_topicos,
                   random_state=SEED, passes=10, iterations=100)

    linhas = []
    for topico, termos in lda.show_topics(num_topics=n_topicos, num_words=12,
                                          formatted=False):
        linhas.append({
            "topico": topico,
            "termos": ", ".join(palavra for palavra, _ in termos),
        })
    tabela = pd.DataFrame(linhas)
    ETAPA3.mkdir(parents=True, exist_ok=True)
    saida = ETAPA3 / "topicos_lda.csv"
    tabela.to_csv(saida, index=False)
    print(f"{n_topicos} tópicos LDA em {saida}")
    print("Próximo passo qualitativo: cruzar os tópicos com as nove famílias.")
    return tabela


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metodo", choices=["lda", "bertopic"], default="lda")
    parser.add_argument("--n-topicos", type=int, default=15)
    args = parser.parse_args()

    meta = pd.read_csv(METADATA_CSV)
    if "incluido" in meta.columns:
        meta = meta[meta["incluido"] == True]  # noqa: E712
    textos = meta["abstract"].fillna("").tolist()
    ETAPA3.mkdir(parents=True, exist_ok=True)
    print(f"Seed fixo: {SEED}. Método: {args.metodo}. Tópicos: {args.n_topicos}.")

    if args.metodo == "lda":
        rodar_lda(textos, args.n_topicos)
    else:
        raise NotImplementedError("BERTopic: instalar extra `topic` e implementar.")


if __name__ == "__main__":
    main()
