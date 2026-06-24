"""Etapa 1: importa exportações de bases bibliográficas e consolida metadados.

Lê exportações brutas das bases e escreve um CSV consolidado em
`corpus/metadata/corpus_metadata.csv`, no esquema descrito em `corpus/README.md`.
Aceita múltiplas fontes numa só execução (uma por base) e empilha os registros;
a deduplicação fica para `02_dedup.py`.

Formatos suportados:
    wos     Web of Science *tab-delimited* (WoS Core, exportação "Tab-delimited").
    scopus  Scopus CSV (exportação "CSV").
    ris     RIS (Scopus/WoS via RIS), quando `rispy` está instalado.

Uso:
    python scripts/01_import_wos.py --fonte corpus/exports/wos_2026-06.txt --base wos
    python scripts/01_import_wos.py \\
        --fonte corpus/exports/wos.txt --base wos \\
        --fonte corpus/exports/scopus.csv --base scopus
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import pandas as pd

from _paths import METADATA_CSV, exports_dir

# Esquema-alvo (corpus/README.md). A ordem fixa estabiliza o CSV versionado.
COLUNAS = [
    "id",
    "doi",
    "titulo",
    "autores",
    "ano",
    "fonte",
    "base",
    "categoria_wos",
    "tipo_doc",
    "idioma",
    "citacoes",
    "abstract",
    "incluido",
    "motivo_exclusao",
    "no_subcorpus",
]

# Mapa de idiomas das bases (rótulo nativo -> código ISO de duas letras).
_IDIOMA = {
    "english": "en",
    "portuguese": "pt",
    "spanish": "es",
    "castilian": "es",
}


def normalizar_doi(valor: object) -> str:
    """Normaliza DOI: minúsculas, sem prefixo de URL nem espaços."""
    s = str(valor or "").strip().lower()
    s = re.sub(r"^https?://(dx\.)?doi\.org/", "", s)
    s = re.sub(r"^doi:\s*", "", s)
    return s


def normalizar_idioma(valor: object) -> str:
    """Mapeia o idioma nativo da base para código ISO; vazio se desconhecido."""
    return _IDIOMA.get(str(valor or "").strip().lower(), "")


def _to_int(valor: object) -> int:
    """Converte para inteiro tolerando vazio e ruído; 0 como neutro."""
    m = re.search(r"\d+", str(valor or ""))
    return int(m.group()) if m else 0


def ler_wos_tab(fonte: Path) -> pd.DataFrame:
    """Lê exportação WoS *tab-delimited* e mapeia as tags de campo ao esquema.

    Tags WoS usadas: DI (DOI), TI (título), AU (autores), PY (ano), SO (fonte),
    WC (categorias), DT (tipo), LA (idioma), TC (citações), AB (resumo).
    """
    df = pd.read_csv(fonte, sep="\t", dtype=str, quoting=csv.QUOTE_NONE,
                     on_bad_lines="skip", encoding="utf-8-sig").fillna("")
    return pd.DataFrame({
        "doi": df.get("DI", "").map(normalizar_doi),
        "titulo": df.get("TI", ""),
        "autores": df.get("AU", "").map(lambda s: str(s).replace("\n", "; ")),
        "ano": df.get("PY", "").map(_to_int),
        "fonte": df.get("SO", ""),
        "categoria_wos": df.get("WC", ""),
        "tipo_doc": df.get("DT", "").map(_titlecase_tipo),
        "idioma": df.get("LA", "").map(normalizar_idioma),
        "citacoes": df.get("TC", "").map(_to_int),
        "abstract": df.get("AB", ""),
    })


def ler_scopus_csv(fonte: Path) -> pd.DataFrame:
    """Lê exportação Scopus CSV e mapeia os cabeçalhos ao esquema.

    Cabeçalhos Scopus usados: DOI, Title, Authors, Year, Source title,
    Document Type, Language of Original Document, Cited by, Abstract.
    """
    df = pd.read_csv(fonte, dtype=str).fillna("")
    return pd.DataFrame({
        "doi": df.get("DOI", "").map(normalizar_doi),
        "titulo": df.get("Title", ""),
        "autores": df.get("Authors", ""),
        "ano": df.get("Year", "").map(_to_int),
        "fonte": df.get("Source title", ""),
        "categoria_wos": "",  # Scopus não traz a categoria WoS; fica vazia.
        "tipo_doc": df.get("Document Type", "").map(_titlecase_tipo),
        "idioma": df.get("Language of Original Document", "").map(normalizar_idioma),
        "citacoes": df.get("Cited by", "").map(_to_int),
        "abstract": df.get("Abstract", ""),
    })


def ler_ris(fonte: Path) -> pd.DataFrame:
    """Lê arquivo RIS via `rispy` e mapeia as tags ao esquema."""
    try:
        import rispy
    except ImportError as erro:  # dependência opcional
        raise SystemExit(
            "Leitura de RIS exige `rispy` (pip install rispy)."
        ) from erro

    with open(fonte, encoding="utf-8") as fh:
        entradas = rispy.load(fh)

    tipo_ris = {"JOUR": "Article", "CONF": "Proceedings Paper", "CPAPER":
                "Proceedings Paper", "RPRT": "Report", "CHAP": "Book Chapter"}
    linhas = []
    for e in entradas:
        autores = e.get("authors") or e.get("first_authors") or []
        linhas.append({
            "doi": normalizar_doi(e.get("doi", "")),
            "titulo": e.get("title", "") or e.get("primary_title", ""),
            "autores": "; ".join(autores),
            "ano": _to_int(e.get("year", "") or e.get("publication_year", "")),
            "fonte": e.get("journal_name", "") or e.get("secondary_title", ""),
            "categoria_wos": "",
            "tipo_doc": tipo_ris.get(e.get("type_of_reference", ""), "Article"),
            "idioma": normalizar_idioma(e.get("language", "")),
            "citacoes": 0,
            "abstract": e.get("abstract", ""),
        })
    return pd.DataFrame(linhas)


def _titlecase_tipo(valor: object) -> str:
    """Normaliza o tipo de documento para a forma do esquema (Title Case)."""
    s = str(valor or "").strip().lower()
    mapa = {
        "article": "Article",
        "review": "Review",
        "proceedings paper": "Proceedings Paper",
        "conference paper": "Proceedings Paper",
        "book chapter": "Book Chapter",
    }
    return mapa.get(s, s.title() if s else "")


_LEITORES = {
    "wos": ler_wos_tab,
    "scopus": ler_scopus_csv,
    "ris": ler_ris,
}


def importar(fonte: Path, base: str) -> pd.DataFrame:
    """Lê uma exportação e a normaliza para o esquema do corpus.

    Args:
        fonte: caminho do arquivo exportado.
        base: identificador da base/formato (wos, scopus, ris).

    Returns:
        DataFrame no esquema de `corpus_metadata.csv`, sem `id` (atribuído ao
        consolidar) e com as colunas de estado da Etapa 1 ainda vazias.
    """
    leitor = _LEITORES.get(base)
    if leitor is None:
        raise ValueError(f"Base/formato não suportado: {base}. Use {list(_LEITORES)}.")
    df = leitor(fonte)
    df["base"] = "scopus" if base == "scopus" else ("wos" if base == "wos" else "ris")
    return df


def consolidar(frames: list[pd.DataFrame]) -> pd.DataFrame:
    """Empilha as fontes, atribui `id` estável e completa as colunas do esquema."""
    df = pd.concat(frames, ignore_index=True)
    df["id"] = [f"art{n:06d}" for n in range(1, len(df) + 1)]
    df["incluido"] = pd.NA
    df["motivo_exclusao"] = ""
    df["no_subcorpus"] = False
    return df.reindex(columns=COLUNAS)


def _resolver(fonte: Path) -> Path:
    """Resolve a fonte: usa o caminho dado ou procura em exports_dir()."""
    if fonte.exists():
        return fonte
    candidato = exports_dir() / fonte.name
    if candidato.exists():
        return candidato
    raise FileNotFoundError(
        f"Exportação não encontrada: {fonte} (nem em {exports_dir()})."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fonte", type=Path, action="append", required=True,
                        help="arquivo exportado (repetível, pareado com --base)")
    parser.add_argument("--base", action="append", required=True,
                        choices=["wos", "scopus", "ris"],
                        help="base/formato da fonte correspondente (repetível)")
    args = parser.parse_args()

    if len(args.fonte) != len(args.base):
        parser.error("número de --fonte e --base deve coincidir (pares ordenados).")

    frames = []
    for fonte, base in zip(args.fonte, args.base):
        caminho = _resolver(fonte)
        df = importar(caminho, base)
        print(f"  {base}: {len(df)} registros de {caminho}")
        frames.append(df)

    consolidado = consolidar(frames)
    METADATA_CSV.parent.mkdir(parents=True, exist_ok=True)
    consolidado.to_csv(METADATA_CSV, index=False)
    print(f"{len(consolidado)} registros consolidados em {METADATA_CSV}")
    print("Próximo passo: python scripts/02_dedup.py")


if __name__ == "__main__":
    main()
