"""Etapa 2, nível 1: codificação lexical por família semântica.

Conta ocorrências de cada família do catálogo (`campos_lexicais/
catalogo_familias.yaml`) sobre o texto disponível de cada artigo (resumo, ou
texto integral quando presente em `fulltext_dir()`). Produz a matriz artigo ×
família, em versão bruta. Para as famílias marcadas com `desambiguar: true`
(antropomorfica, militar), a versão refinada é aplicada por
`04b_desambiguar.py` a partir do CSV manual, nunca recomputada aqui.

A lista de termos é escolhida pela coluna `idioma` do artigo (decisão 2.c, corpus
en+pt+es): en usa `termos`, pt usa `termos_pt`, es usa `termos_es`, com recuo para
`termos` quando a lista da língua falta no catálogo. Os termos pt/es são rascunho a
validar (ver cabeçalho do catálogo).

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


# Idiomas suportados e as chaves de termos/exclusões correspondentes no catálogo.
IDIOMAS = ("en", "pt", "es")
_CHAVE_TERMOS = {"en": "termos", "pt": "termos_pt", "es": "termos_es"}
_CHAVE_EXCLUSOES = {"en": "exclusoes", "pt": "exclusoes_pt", "es": "exclusoes_es"}


def termos_da_familia(meta: dict, idioma: str) -> list[str]:
    """Lista de termos de uma família na língua dada, com recuo para o inglês."""
    return meta.get(_CHAVE_TERMOS.get(idioma, "termos")) or meta["termos"]


def exclusoes_da_familia(meta: dict, idioma: str) -> list[str] | None:
    """Exclusões de uma família na língua dada, com recuo para o inglês."""
    return meta.get(_CHAVE_EXCLUSOES.get(idioma, "exclusoes")) or meta.get("exclusoes")


def compilar_por_idioma(catalogo: dict) -> dict[str, dict[str, tuple]]:
    """Pré-compila (padrão, exclusão) por idioma e família."""
    tabela: dict[str, dict[str, tuple]] = {}
    for idioma in IDIOMAS:
        tabela[idioma] = {}
        for fam, meta in catalogo.items():
            padrao = compilar_padroes(termos_da_familia(meta, idioma))
            excl = exclusoes_da_familia(meta, idioma)
            tabela[idioma][fam] = (padrao, compilar_padroes(excl) if excl else None)
    return tabela


# Janela de contexto (palavras de cada lado) para testar as exclusões do catálogo.
JANELA_EXCLUSAO = 5


def contar(texto: str, padrao: re.Pattern, exclusao: re.Pattern | None = None) -> int:
    """Conta ocorrências de um padrão, descartando as que casam uma exclusão.

    Uma ocorrência é descartada quando o padrão de exclusão casa no trecho central
    ou nas `JANELA_EXCLUSAO` palavras adjacentes de cada lado, conforme a semântica
    documentada no catálogo (ex.: 'network' precedido de 'neural').
    """
    texto = str(texto)
    if exclusao is None:
        return len(padrao.findall(texto))

    palavras = re.findall(r"\S+", texto)
    total = 0
    for m in padrao.finditer(texto):
        ini_palavra = len(re.findall(r"\S+", texto[: m.start()]))
        janela = palavras[max(0, ini_palavra - JANELA_EXCLUSAO):
                          ini_palavra + JANELA_EXCLUSAO + 1]
        if not exclusao.search(" ".join(janela)):
            total += 1
    return total


def codificar(df: pd.DataFrame, catalogo: dict) -> pd.DataFrame:
    """Gera a matriz artigo × família (contagem bruta sobre o resumo).

    Escolhe a lista de termos pela coluna `idioma` do artigo e aplica o campo
    `exclusoes` da mesma língua quando presente, removendo ocorrências cujo contexto
    casa uma expressão de exclusão.
    """
    tabela = compilar_por_idioma(catalogo)
    familias = list(catalogo.keys())
    linhas = []
    for _, art in df.iterrows():
        texto = art.get("abstract", "")
        idioma = str(art.get("idioma", "en") or "en").lower()
        por_familia = tabela.get(idioma, tabela["en"])
        linha = {"id": art["id"]}
        for fam in familias:
            padrao, exclusao = por_familia[fam]
            linha[fam] = contar(texto, padrao, exclusao)
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
