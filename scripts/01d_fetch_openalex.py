"""Etapa 1, re-coleta: baixa os works da OpenAlex por ID e grava JSONL.

Lê uma planilha que tenha a coluna `openalex_id` (por exemplo o corpus já filtrado
`openalex_ia_humanas_corpus_BR.csv`), busca cada obra na API aberta da OpenAlex em
lotes, pedindo o `abstract_inverted_index`, e escreve um JSONL de works no formato
que `01_import_wos.py --base openalex` consome (com reconstrução de resumo).

Roda na máquina da pesquisadora (a API da OpenAlex não sai do contêiner remoto).
Sem chave; só um e-mail para o pool educado.

Uso:
    python scripts/01d_fetch_openalex.py \\
        --corpus ~/bibliometria-ia-humanas/dados_openalex/openalex_ia_humanas_corpus_BR.csv \\
        --saida works_para_tramar.jsonl --email voce@unicamp.br
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import pandas as pd
import requests

API = "https://api.openalex.org/works"
SELECT = ",".join(
    [
        "id",
        "doi",
        "title",
        "display_name",
        "publication_year",
        "language",
        "type",
        "cited_by_count",
        "authorships",
        "primary_topic",
        "abstract_inverted_index",
    ]
)
LOTE = 50
TIMEOUT = 60


def short_id(valor: object) -> str:
    """Extrai o id curto da OpenAlex (W seguido de dígitos) de URL ou texto."""
    m = re.search(r"W\d+", str(valor or ""))
    return m.group(0) if m else ""


def ler_ids(corpus: Path, coluna: str) -> list[str]:
    """Lê a coluna de ids da planilha (CSV ou XLSX) e devolve ids curtos únicos."""
    if corpus.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(corpus)
    else:
        df = pd.read_csv(corpus)
    if coluna not in df.columns:
        raise SystemExit(f"Coluna '{coluna}' não está em {corpus}. Colunas: {list(df.columns)}")
    ids = {short_id(v) for v in df[coluna]}
    return sorted(i for i in ids if i)


def baixar(ids: list[str], email: str, saida: Path) -> tuple[int, int]:
    """Baixa os works em lotes e grava um por linha no JSONL. Retorna (achados, total)."""
    achados = 0
    with open(saida, "w", encoding="utf-8") as fh:
        for inicio in range(0, len(ids), LOTE):
            lote = ids[inicio : inicio + LOTE]
            params = {
                "filter": "openalex_id:" + "|".join(lote),
                "select": SELECT,
                "per-page": LOTE,
                "mailto": email,
            }
            resp = requests.get(API, params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            for work in resp.json().get("results", []):
                fh.write(json.dumps(work, ensure_ascii=False) + "\n")
                achados += 1
            print(f"  {min(inicio + LOTE, len(ids))}/{len(ids)} ids processados", flush=True)
            time.sleep(0.2)  # pool educado, abaixo do limite da OpenAlex
    return achados, len(ids)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus", type=Path, required=True, help="planilha com a coluna openalex_id (CSV ou XLSX)"
    )
    parser.add_argument("--saida", type=Path, default=Path("works_para_tramar.jsonl"))
    parser.add_argument("--coluna", default="openalex_id", help="nome da coluna de id")
    parser.add_argument("--email", required=True, help="e-mail para o pool educado")
    args = parser.parse_args()

    ids = ler_ids(args.corpus, args.coluna)
    if not ids:
        raise SystemExit("Nenhum openalex_id válido encontrado na planilha.")
    print(f"{len(ids)} ids a baixar da OpenAlex...")

    achados, total = baixar(ids, args.email, args.saida)
    com_resumo = _contar_com_resumo(args.saida)
    print(f"\n{achados}/{total} works baixados em {args.saida}")
    print(f"{com_resumo} com abstract_inverted_index (resumo reconstruível).")
    print("Próximo: python scripts/01_import_wos.py --fonte " f"{args.saida} --base openalex")


def _contar_com_resumo(saida: Path) -> int:
    """Conta quantos works no JSONL trazem abstract_inverted_index."""
    n = 0
    with open(saida, encoding="utf-8") as fh:
        for linha in fh:
            if linha.strip() and json.loads(linha).get("abstract_inverted_index"):
                n += 1
    return n


if __name__ == "__main__":
    main()
