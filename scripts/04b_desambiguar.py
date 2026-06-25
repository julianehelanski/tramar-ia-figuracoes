"""Etapa 2, refinamento: desambiguação manual das famílias homônimas.

As famílias marcadas com `desambiguar: true` no catálogo (antropomorfica,
militar) misturam uso técnico-literal e uso figurativo do mesmo termo
(`attention`, `memory`, `deploy`, `target`). A contagem lexical bruta de
`04_lexical_coding.py` superestima a figuração nessas famílias. Este passo separa
as duas leituras por uma camada manual auditável, no molde da desambiguação
war/wars do projeto `analise-figuracoes-latour` (decisão 3 em
`docs/decisoes_metodologicas.md`).

Fluxo em duas fases:

    --gerar   varre os resumos e escreve, por família, um CSV de ocorrências com
              contexto KWIC e a coluna `categoria_final` em branco, para Juliane
              classificar (valores: figurativa | tecnica). Não sobrescreve um CSV
              já existente; a camada manual nunca é recomputada.

    --aplicar (padrão) lê os CSV classificados e gera
              `codificacao_lexical_refinada.csv`: as colunas das famílias
              desambiguadas passam a contar apenas as ocorrências marcadas como
              `figurativa`; as demais famílias são copiadas da versão bruta.

Uso:
    python scripts/04b_desambiguar.py --gerar
    python scripts/04b_desambiguar.py            # aplicar
"""

from __future__ import annotations

import argparse

# Reaproveita a compilação de padrões e a janela de exclusão do passo lexical.
import importlib.util
import re
from pathlib import Path

import pandas as pd
import yaml
from _paths import CATALOGO_PATH, ETAPA2, METADATA_CSV

_spec = importlib.util.spec_from_file_location(
    "_lexical", Path(__file__).resolve().parent / "04_lexical_coding.py"
)
_lex = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_lex)
compilar_padroes = _lex.compilar_padroes
termos_da_familia = _lex.termos_da_familia
IDIOMAS = _lex.IDIOMAS

# Janela KWIC (palavras de cada lado) registrada no contexto de classificação.
JANELA_KWIC = 8
# Três vias: só `figurativa` (predicado atribuído à IA) conta na matriz refinada.
# `tecnica` (termo sedimentado) e `literal` (cognição humana, não da IA) são excluídas.
CATEGORIAS_VALIDAS = {"figurativa", "tecnica", "literal"}


def carregar_catalogo() -> dict:
    """Carrega o catálogo de famílias do YAML."""
    with open(CATALOGO_PATH, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def familias_desambiguar(catalogo: dict) -> list[str]:
    """Lista as famílias marcadas com `desambiguar: true`."""
    return [fam for fam, meta in catalogo.items() if meta.get("desambiguar")]


def caminho_csv(familia: str) -> Path:
    """Caminho do CSV manual de classificação de uma família."""
    return ETAPA2 / f"desambiguacao_{familia}.csv"


def _kwic(texto: str, ini: int, fim: int) -> str:
    """Extrai janela KWIC de `JANELA_KWIC` palavras em torno de um trecho."""
    antes = re.findall(r"\S+", texto[:ini])[-JANELA_KWIC:]
    centro = texto[ini:fim]
    depois = re.findall(r"\S+", texto[fim:])[:JANELA_KWIC]
    return f"{' '.join(antes)} [[{centro}]] {' '.join(depois)}".strip()


def extrair_ocorrencias(df: pd.DataFrame, catalogo: dict, familia: str) -> pd.DataFrame:
    """Tabela de ocorrências (uma linha por casamento) com contexto KWIC.

    Escolhe a lista de termos pela coluna `idioma` de cada artigo (decisão 2.c).
    """
    meta = catalogo[familia]
    padrao_por_idioma = {idi: compilar_padroes(termos_da_familia(meta, idi)) for idi in IDIOMAS}
    linhas = []
    for _, art in df.iterrows():
        texto = str(art.get("abstract", "") or "")
        idioma = str(art.get("idioma", "en") or "en").lower()
        padrao = padrao_por_idioma.get(idioma, padrao_por_idioma["en"])
        for m in padrao.finditer(texto):
            linhas.append(
                {
                    "id": art["id"],
                    "familia": familia,
                    "termo": m.group(0),
                    "contexto": _kwic(texto, m.start(), m.end()),
                    "categoria_sugerida": "",
                    "categoria_final": "",
                }
            )
    return pd.DataFrame(
        linhas,
        columns=["id", "familia", "termo", "contexto", "categoria_sugerida", "categoria_final"],
    )


def gerar(df: pd.DataFrame, catalogo: dict) -> None:
    """Escreve os CSV de classificação em branco, sem sobrescrever existentes."""
    for familia in familias_desambiguar(catalogo):
        destino = caminho_csv(familia)
        if destino.exists():
            print(f"  {familia}: {destino.name} já existe, preservado.")
            continue
        ocs = extrair_ocorrencias(df, catalogo, familia)
        destino.parent.mkdir(parents=True, exist_ok=True)
        ocs.to_csv(destino, index=False)
        print(
            f"  {familia}: {len(ocs)} ocorrências em {destino.name} "
            "(preencher coluna categoria_final: figurativa | tecnica)."
        )


def aplicar(catalogo: dict) -> pd.DataFrame:
    """Gera a matriz refinada a partir dos CSV classificados.

    Para cada família desambiguada, a coluna passa a contar por artigo as
    ocorrências com `categoria_final == figurativa`. Ocorrências sem classificação
    são reportadas e não entram na contagem refinada.
    """
    bruta = pd.read_csv(ETAPA2 / "codificacao_lexical.csv")
    refinada = bruta.copy()

    for familia in familias_desambiguar(catalogo):
        origem = caminho_csv(familia)
        if not origem.exists():
            raise SystemExit(
                f"Falta {origem}. Rode primeiro: python scripts/04b_desambiguar.py "
                "--gerar e classifique a coluna categoria_final."
            )
        ocs = pd.read_csv(origem).fillna({"categoria_final": ""})
        final = ocs["categoria_final"].astype(str).str.strip().str.lower()

        invalidas = set(final.unique()) - CATEGORIAS_VALIDAS - {""}
        if invalidas:
            raise SystemExit(
                f"{origem.name}: valores inválidos em categoria_final: {invalidas}. "
                f"Use {sorted(CATEGORIAS_VALIDAS)}."
            )
        nao_classificadas = int((final == "").sum())
        if nao_classificadas:
            print(
                f"  {familia}: {nao_classificadas} ocorrências sem classificação "
                "(excluídas da contagem refinada)."
            )

        figurativas = ocs.loc[final == "figurativa", "id"].value_counts()
        refinada[familia] = refinada["id"].map(figurativas).fillna(0).astype(int)
        print(
            f"  {familia}: {int(figurativas.sum())} ocorrências figurativas "
            f"(bruta: {int(bruta[familia].sum())})."
        )

    return refinada


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--gerar", action="store_true", help="gerar os CSV de classificação em branco"
    )
    args = parser.parse_args()

    catalogo = carregar_catalogo()

    if args.gerar:
        df = pd.read_csv(METADATA_CSV)
        df = df[df["incluido"] == True] if "incluido" in df.columns else df  # noqa: E712
        gerar(df, catalogo)
        print("Classifique os CSV e rode: python scripts/04b_desambiguar.py")
        return

    refinada = aplicar(catalogo)
    saida = ETAPA2 / "codificacao_lexical_refinada.csv"
    refinada.to_csv(saida, index=False)
    print(f"Matriz refinada em {saida}")
    print("Os passos 05 e 06 podem ler a versão refinada quando ela existir.")


if __name__ == "__main__":
    main()
