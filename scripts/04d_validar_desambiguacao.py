"""Etapa 2, validação: amostra para conferir o passe automático da desambiguação.

Sorteia, de cada CSV de desambiguação já sugerido por `04c`, uma amostra
estratificada por confiança (metade de alta, metade de baixa), com `seed=42`, e
escreve `validacao_<familia>.csv` com uma coluna `correto` em branco (s/n) para a
pesquisadora marcar se a sugestão automática acertou. Reproduzível.

Depois de marcar, rodar com `--avaliar` calcula a acurácia da heurística por família
e por confiança, para decidir se o passe automático se sustenta ou precisa de mais
revisão manual.

Uso:
    python scripts/04d_validar_desambiguacao.py --n 40      # gera as amostras
    python scripts/04d_validar_desambiguacao.py --avaliar   # mede a acurácia
"""

from __future__ import annotations

import argparse

import pandas as pd
from _paths import ETAPA2, SEED

COLS = ["id", "termo", "contexto", "categoria_sugerida", "confianca", "motivo"]


def caminho_validacao(familia: str):
    """Caminho do CSV de validação de uma família."""
    return ETAPA2 / f"validacao_{familia}.csv"


def gerar(n: int) -> None:
    """Escreve uma amostra estratificada por confiança para cada família."""
    csvs = sorted(ETAPA2.glob("desambiguacao_*.csv"))
    if not csvs:
        raise SystemExit("Rode antes 04b --gerar e 04c (para ter as sugestões).")
    for caminho in csvs:
        familia = caminho.stem.replace("desambiguacao_", "")
        df = pd.read_csv(caminho)
        if "confianca" not in df.columns:
            raise SystemExit(f"{caminho.name} sem coluna 'confianca'; rode 04c antes.")
        partes = []
        for conf in ("alta", "baixa"):
            sub = df[df["confianca"] == conf]
            partes.append(sub.sample(min(n // 2, len(sub)), random_state=SEED))
        amostra = pd.concat(partes).reset_index(drop=True)
        amostra = amostra.reindex(columns=COLS)
        amostra["correto"] = ""  # preencher: s (acertou) | n (errou)
        amostra["categoria_corrigida"] = ""  # se errou, a categoria certa
        destino = caminho_validacao(familia)
        amostra.to_csv(destino, index=False)
        print(
            f"{familia}: {len(amostra)} linhas em {destino.name} "
            "(preencher coluna 'correto' com s ou n)."
        )
    print(
        "\nMarque a coluna 'correto' e rode: python scripts/04d_validar_desambiguacao.py --avaliar"
    )


def avaliar() -> None:
    """Lê as amostras marcadas e reporta a acurácia da heurística."""
    csvs = sorted(ETAPA2.glob("validacao_*.csv"))
    if not csvs:
        raise SystemExit("Nenhum validacao_*.csv; rode antes sem --avaliar para gerar.")
    for caminho in csvs:
        familia = caminho.stem.replace("validacao_", "")
        df = pd.read_csv(caminho)
        marcado = df[df["correto"].astype(str).str.strip().str.lower().isin(["s", "n"])]
        if marcado.empty:
            print(f"{familia}: nenhuma linha marcada ainda.")
            continue
        certo = marcado["correto"].astype(str).str.strip().str.lower().eq("s")
        print(f"\n=== {familia}: {len(marcado)} linhas conferidas ===")
        print(f"  acurácia geral: {certo.mean():.0%}")
        for conf in ("alta", "baixa"):
            m = marcado[marcado["confianca"] == conf]
            if len(m):
                acc = m["correto"].astype(str).str.strip().str.lower().eq("s").mean()
                print(f"  confiança {conf}: {acc:.0%} ({len(m)} linhas)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=40, help="tamanho da amostra por família")
    parser.add_argument("--avaliar", action="store_true", help="medir a acurácia das marcações")
    args = parser.parse_args()
    if args.avaliar:
        avaliar()
    else:
        gerar(args.n)


if __name__ == "__main__":
    main()
