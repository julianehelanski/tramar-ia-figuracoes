"""Etapa 1, raspagem: baixa da OpenAlex obras de IA por filtro, com resumo.

Coleta pela API aberta da OpenAlex e grava um JSONL de works no formato que
`01_import_wos.py --base openalex` consome (com `abstract_inverted_index`, do qual o
resumo é reconstruído).

Dois modos:
- Censo (padrão): pagina por cursor todas as obras do filtro. Imprime a contagem
  antes e tem limite de segurança contra coletas gigantes.
- Amostra (--amostra N): usa a amostragem aleatória da OpenAlex (sample + seed) para
  baixar N obras sorteadas (máximo 10.000 por chamada). Reprodutível por `--seed`.

Pensado para o corpus de IA em TODAS as áreas, que dá o contraste técnico contra
crítico. Para amostra estratificada por polo, use --fields restringindo o estrato
(técnico: 17|22 = Computação e Engenharia; crítico: 12|33 = Humanas e Sociais) e
rode uma vez por polo, com o mesmo --seed.

Roda na máquina da pesquisadora (a API da OpenAlex não sai do contêiner remoto).
Sem chave; só um e-mail para o pool educado.

Uso:
    # amostra estratificada (rode os dois e importe juntos):
    python scripts/01e_scrape_openalex.py --amostra 5000 --fields "17|22" \\
        --email voce@unicamp.br --saida works_tecnico.jsonl
    python scripts/01e_scrape_openalex.py --amostra 5000 --fields "12|33" \\
        --email voce@unicamp.br --saida works_critico.jsonl
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
LIMITE_SEGURO = 300_000  # acima disso, o censo exige --forcar
MAX_AMOSTRA = 10_000  # teto da amostragem da OpenAlex por chamada


def montar_filtro(
    concept: str,
    ano_ini: int,
    ano_fim: int,
    pais: str | None,
    fields: str | None,
    busca: str | None = None,
) -> str:
    """Monta o filtro da OpenAlex (vírgula = E).

    Com `busca`, acrescenta uma busca de texto em título e resumo
    (`title_and_abstract.search`), para o corpus metalinguístico restritivo: artigos
    de IA que tematizam metáfora, figuração, tropo, antropomorfização.
    """
    partes = [
        f"concepts.id:{concept}",
        f"from_publication_date:{ano_ini}-01-01",
        f"to_publication_date:{ano_fim}-12-31",
    ]
    if fields:
        partes.append(f"primary_topic.field.id:{fields}")
    if pais:
        partes.append(f"authorships.countries:{pais.upper()}")
    if busca:
        partes.append(f"title_and_abstract.search:{busca}")
    return ",".join(partes)


def contar(filtro: str, email: str) -> int:
    """Retorna quantas obras o filtro tem (meta.count), sem baixar tudo."""
    params = {"filter": filtro, "per-page": 1, "mailto": email}
    resp = requests.get(API, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    return int(resp.json().get("meta", {}).get("count", 0))


def _gravar(fh, works: list[dict]) -> tuple[int, int]:
    """Escreve os works no JSONL e conta total e quantos têm resumo."""
    baixados = com_resumo = 0
    for work in works:
        fh.write(json.dumps(work, ensure_ascii=False) + "\n")
        baixados += 1
        if work.get("abstract_inverted_index"):
            com_resumo += 1
    return baixados, com_resumo


def raspar_censo(filtro: str, email: str, saida: str) -> tuple[int, int]:
    """Pagina por cursor todas as obras do filtro."""
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
            b, c = _gravar(fh, resultados)
            baixados += b
            com_resumo += c
            cursor = data.get("meta", {}).get("next_cursor")
            sys.stderr.write(f"\r  {baixados:,} obras baixadas")
            sys.stderr.flush()
            if not resultados:
                break
            time.sleep(0.2)
    sys.stderr.write("\n")
    return baixados, com_resumo


def raspar_amostra(filtro: str, n: int, seed: int, email: str, saida: str) -> tuple[int, int]:
    """Baixa N obras sorteadas (sample + seed da OpenAlex), paginando por página."""
    n = min(n, MAX_AMOSTRA)
    baixados = com_resumo = 0
    pagina = 1
    with open(saida, "w", encoding="utf-8") as fh:
        while baixados < n:
            params = {
                "filter": filtro,
                "select": SELECT,
                "sample": n,
                "seed": seed,
                "per-page": PER_PAGE,
                "page": pagina,
                "mailto": email,
            }
            resp = requests.get(API, params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            resultados = resp.json().get("results", [])
            if not resultados:
                break
            b, c = _gravar(fh, resultados)
            baixados += b
            com_resumo += c
            pagina += 1
            sys.stderr.write(f"\r  {baixados:,}/{n:,} obras amostradas")
            sys.stderr.flush()
            time.sleep(0.2)
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
    parser.add_argument(
        "--busca",
        default=None,
        help="busca metalinguística em título/resumo (ex.: 'metaphor OR figuration OR trope')",
    )
    parser.add_argument(
        "--fields", default=None, help="estrato disciplinar (ex.: '17|22' técnico, '12|33' crítico)"
    )
    parser.add_argument("--amostra", type=int, default=None, help="N obras sorteadas (máx 10000)")
    parser.add_argument("--seed", type=int, default=42, help="semente da amostragem")
    parser.add_argument(
        "--forcar", action="store_true", help="ignora o limite de segurança do censo"
    )
    args = parser.parse_args()

    filtro = montar_filtro(
        args.concept, args.ano_inicial, args.ano_final, args.pais, args.fields, args.busca
    )
    escopo = args.pais.upper() if args.pais else "global"
    estrato = f" | fields {args.fields}" if args.fields else ""
    print(f"Filtro: {filtro}")
    print(f"Escopo: IA | {escopo} | {args.ano_inicial}-{args.ano_final}{estrato}")

    total = contar(filtro, args.email)
    print(f"O filtro retorna {total:,} obras na população.")

    if args.amostra is not None:
        n = min(args.amostra, MAX_AMOSTRA)
        if args.amostra > MAX_AMOSTRA:
            print(f"Amostra limitada a {MAX_AMOSTRA:,} (teto da OpenAlex por chamada).")
        print(f"Amostrando {n:,} obras (seed={args.seed})...")
        baixados, com_resumo = raspar_amostra(filtro, n, args.seed, args.email, args.saida)
    else:
        if total > LIMITE_SEGURO and not args.forcar:
            raise SystemExit(
                f"São {total:,} obras (acima de {LIMITE_SEGURO:,}). Use --amostra N para "
                "uma amostra, ou --forcar para o censo, ou estreite com --pais/--fields/anos."
            )
        baixados, com_resumo = raspar_censo(filtro, args.email, args.saida)

    print(f"\n{baixados:,} obras gravadas em {args.saida}")
    print(f"{com_resumo:,} com abstract_inverted_index (resumo reconstruível).")
    print(f"Próximo: python scripts/01_import_wos.py --fonte {args.saida} --base openalex")


if __name__ == "__main__":
    main()
