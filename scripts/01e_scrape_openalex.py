"""Etapa 1, raspagem: baixa da OpenAlex todas as obras de IA por filtro, com resumo.

Faz a coleta nova e completa pela API aberta da OpenAlex, paginando por cursor, e
grava um JSONL de works no formato que `01_import_wos.py --base openalex` consome
(com `abstract_inverted_index`, do qual o resumo é reconstruído).

Pensado para o corpus de IA em TODAS as áreas (sem o recorte de humanidades), que dá
o contraste técnico contra crítico do projeto. O filtro é montável por argumento:
conceito de IA, janela de anos e, opcionalmente, país. Antes de baixar, imprime
quantas obras o filtro retorna, para dimensionar o download e evitar coletas
gigantes por engano.

Roda na máquina da pesquisadora (a API da OpenAlex não sai do contêiner remoto).
Sem chave; só um e-mail para o pool educado.

Uso:
    # IA em todas as áreas, Brasil, 2015-2026 (reproduz a ordem de grandeza de ~98 mil):
    python scripts/01e_scrape_openalex.py --pais BR --email voce@unicamp.br \\
        --saida works_todas_areas_BR.jsonl

    # IA em todas as áreas, global (CUIDADO: milhões de obras; exige --forcar):
    python scripts/01e_scrape_openalex.py --email voce@unicamp.br --saida works_global.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
import time

import requests

API = "https://api.openalex.org/works"
# Conceito "Artificial Intelligence" da OpenAlex (engloba ML/DL como subconceitos).
CONCEITO_IA = "C154945302"
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
PER_PAGE = 200
TIMEOUT = 60
LIMITE_SEGURO = 300_000  # acima disso, exige --forcar para evitar coleta gigante


def montar_filtro(concept: str, ano_ini: int, ano_fim: int, pais: str | None) -> str:
    """Monta o filtro da OpenAlex (vírgula = E)."""
    partes = [
        f"concepts.id:{concept}",
        f"from_publication_date:{ano_ini}-01-01",
        f"to_publication_date:{ano_fim}-12-31",
    ]
    if pais:
        partes.append(f"authorships.countries:{pais.upper()}")
    return ",".join(partes)


def contar(filtro: str, email: str) -> int:
    """Retorna quantas obras o filtro tem (meta.count), sem baixar tudo."""
    params = {"filter": filtro, "per-page": 1, "mailto": email}
    resp = requests.get(API, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    return int(resp.json().get("meta", {}).get("count", 0))


def raspar(filtro: str, email: str, saida: str) -> tuple[int, int]:
    """Pagina por cursor e grava cada work numa linha do JSONL. (baixados, com_resumo)."""
    baixados = com_resumo = 0
    cursor = "*"
    with open(saida, "w", encoding="utf-8") as fh:
        while cursor:
            params = {
                "filter": filtro,
                "select": SELECT,
                "per-page": PER_PAGE,
                "cursor": cursor,
                "mailto": email,
            }
            resp = requests.get(API, params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            resultados = data.get("results", [])
            for work in resultados:
                fh.write(json.dumps(work, ensure_ascii=False) + "\n")
                baixados += 1
                if work.get("abstract_inverted_index"):
                    com_resumo += 1
            cursor = data.get("meta", {}).get("next_cursor")
            sys.stderr.write(f"\r  {baixados:,} obras baixadas")
            sys.stderr.flush()
            if not resultados:
                break
            time.sleep(0.2)  # pool educado, abaixo do limite da OpenAlex
    sys.stderr.write("\n")
    return baixados, com_resumo


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--email", required=True, help="e-mail para o pool educado")
    parser.add_argument("--saida", default="works_todas_areas.jsonl")
    parser.add_argument(
        "--pais", default=None, help="código ISO-2 do país (ex.: BR); vazio = global"
    )
    parser.add_argument("--ano-inicial", type=int, default=2015)
    parser.add_argument("--ano-final", type=int, default=2026)
    parser.add_argument("--concept", default=CONCEITO_IA, help="id do conceito OpenAlex")
    parser.add_argument("--forcar", action="store_true", help="ignora o limite de segurança")
    args = parser.parse_args()

    filtro = montar_filtro(args.concept, args.ano_inicial, args.ano_final, args.pais)
    escopo = args.pais.upper() if args.pais else "global"
    print(f"Filtro: {filtro}")
    print(f"Escopo: IA em todas as áreas | {escopo} | {args.ano_inicial}-{args.ano_final}")

    total = contar(filtro, args.email)
    print(f"O filtro retorna {total:,} obras.")
    if total > LIMITE_SEGURO and not args.forcar:
        raise SystemExit(
            f"São {total:,} obras (acima de {LIMITE_SEGURO:,}). Para baixar mesmo "
            "assim, repita com --forcar; ou estreite com --pais e/ou a janela de anos."
        )

    baixados, com_resumo = raspar(filtro, args.email, args.saida)
    print(f"\n{baixados:,} obras gravadas em {args.saida}")
    print(f"{com_resumo:,} com abstract_inverted_index (resumo reconstruível).")
    print(f"Próximo: python scripts/01_import_wos.py --fonte {args.saida} --base openalex")


if __name__ == "__main__":
    main()
