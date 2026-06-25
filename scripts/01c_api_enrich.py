"""Etapa 1, enriquecimento: completa metadados por DOI via API aberta.

Decisão 2.c híbrida (24/06/2026): o resumo (`abstract`) vem da exportação manual
(Full Record na WoS, CSV na Scopus), porque a API dessas bases só entrega resumo sob
entitlement alto. Os metadados de citação e área disciplinar, ao contrário, vêm por
DOI de uma API acadêmica aberta, sem chave e sem IP institucional, o que dispensa o
VPN e a licença de API das bases pagas.

Provedor padrão: OpenAlex (api.openalex.org), aberto, com cota generosa e busca em
lote por DOI. Alternativa: Crossref (api.crossref.org), uma requisição por DOI.

Acrescenta colunas, sem sobrescrever os campos nativos das bases (auditável):
    citacoes_<prov>   contagem de citações do provedor
    area_<prov>       campo disciplinar do tópico primário (estratificação Etapa 3)
    tipo_<prov>       tipo do documento segundo o provedor

Uso:
    python scripts/01c_api_enrich.py
    python scripts/01c_api_enrich.py --provedor crossref
    python scripts/01c_api_enrich.py --email voce@unicamp.br   # pool educado
"""

from __future__ import annotations

import argparse
import os
import time

import pandas as pd
import requests
from _paths import METADATA_CSV

OPENALEX_URL = "https://api.openalex.org/works"
CROSSREF_URL = "https://api.crossref.org/works/"
LOTE_OPENALEX = 50  # filtro doi:a|b|... aceita vários DOIs por requisição
TIMEOUT = 30


def _email(arg_email: str | None) -> str:
    """E-mail para o pool educado das APIs; do argumento, do .env ou genérico."""
    return arg_email or os.getenv("OPENALEX_EMAIL") or "pesquisa@example.org"


def _norm_doi(valor: object) -> str:
    """DOI em minúsculas sem prefixo de URL (mesma normalização do import).

    Trata NaN, None e os literais 'nan'/'none' como ausência de DOI, porque a
    leitura do CSV traz células vazias como NaN (float, que é truthy).
    """
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return ""
    s = str(valor).strip().lower()
    if s in ("nan", "none"):
        return ""
    for prefixo in ("https://doi.org/", "http://doi.org/", "doi:"):
        if s.startswith(prefixo):
            s = s[len(prefixo) :]
    return s.strip()


def enriquecer_openalex(dois: list[str], email: str) -> dict[str, dict]:
    """Consulta a OpenAlex em lotes e devolve {doi: {citacoes, area, tipo}}."""
    saida: dict[str, dict] = {}
    for inicio in range(0, len(dois), LOTE_OPENALEX):
        lote = dois[inicio : inicio + LOTE_OPENALEX]
        filtro = "doi:" + "|".join(lote)
        params = {"filter": filtro, "per-page": LOTE_OPENALEX, "mailto": email}
        resp = requests.get(OPENALEX_URL, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        for obj in resp.json().get("results", []):
            doi = _norm_doi(obj.get("doi"))
            if not doi:
                continue
            topico = obj.get("primary_topic") or {}
            campo = (topico.get("field") or {}).get("display_name", "")
            saida[doi] = {
                "citacoes": obj.get("cited_by_count"),
                "area": campo,
                "tipo": obj.get("type", ""),
            }
        time.sleep(0.2)  # pool educado, bem abaixo do limite da OpenAlex
    return saida


def enriquecer_crossref(dois: list[str], email: str) -> dict[str, dict]:
    """Consulta a Crossref por DOI (uma requisição cada) e devolve o mesmo mapa."""
    saida: dict[str, dict] = {}
    headers = {"User-Agent": f"tramar-ia-figuracoes (mailto:{email})"}
    for doi in dois:
        resp = requests.get(CROSSREF_URL + doi, headers=headers, timeout=TIMEOUT)
        if resp.status_code != 200:
            continue
        msg = resp.json().get("message", {})
        assuntos = msg.get("subject") or []
        saida[doi] = {
            "citacoes": msg.get("is-referenced-by-count"),
            "area": assuntos[0] if assuntos else "",
            "tipo": msg.get("type", ""),
        }
        time.sleep(0.2)
    return saida


_PROVEDORES = {"openalex": enriquecer_openalex, "crossref": enriquecer_crossref}


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--provedor", choices=list(_PROVEDORES), default="openalex")
    parser.add_argument("--email", default=None, help="e-mail para o pool educado")
    args = parser.parse_args()

    df = pd.read_csv(METADATA_CSV)
    if "doi" not in df.columns:
        raise SystemExit("corpus_metadata.csv sem coluna doi; rode 01_import_wos.py antes.")

    df["_doi_norm"] = df["doi"].map(_norm_doi)
    dois = sorted({d for d in df["_doi_norm"] if d})
    if not dois:
        raise SystemExit("Nenhum DOI no corpus; o enriquecimento por DOI não se aplica.")

    print(f"Enriquecendo {len(dois)} DOIs via {args.provedor}...")
    mapa = _PROVEDORES[args.provedor](dois, _email(args.email))

    prov = args.provedor
    df[f"citacoes_{prov}"] = df["_doi_norm"].map(lambda d: (mapa.get(d) or {}).get("citacoes"))
    df[f"area_{prov}"] = df["_doi_norm"].map(lambda d: (mapa.get(d) or {}).get("area", ""))
    df[f"tipo_{prov}"] = df["_doi_norm"].map(lambda d: (mapa.get(d) or {}).get("tipo", ""))
    df = df.drop(columns="_doi_norm")
    df.to_csv(METADATA_CSV, index=False)

    encontrados = sum(1 for d in dois if d in mapa)
    print(
        f"{encontrados}/{len(dois)} DOIs resolvidos; colunas *_{prov} gravadas em "
        f"{METADATA_CSV}"
    )
    print("O resumo (abstract) continua vindo da exportação manual; nada foi sobrescrito.")


if __name__ == "__main__":
    main()
