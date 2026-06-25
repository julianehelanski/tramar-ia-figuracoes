"""Testes de fumaça do pipeline.

Garantem que o catálogo carrega com as nove famílias e que a seleção de termos por
idioma se comporta como esperado, sem depender de dados de corpus. Servem de
verificação rápida para o hook de SessionStart e contra regressões no catálogo.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[1]


def _carregar(nome: str, arquivo: str):
    """Carrega um módulo de `scripts/` cujo nome de arquivo começa com dígitos."""
    spec = importlib.util.spec_from_file_location(nome, RAIZ / "scripts" / arquivo)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_catalogo_tem_nove_familias():
    cat = yaml.safe_load(
        (RAIZ / "campos_lexicais" / "catalogo_familias.yaml").read_text(encoding="utf-8")
    )
    assert len(cat) == 9
    for familia, meta in cat.items():
        assert meta.get("termos"), f"família {familia} sem termos em inglês"


def test_familias_desambiguar():
    cat = yaml.safe_load(
        (RAIZ / "campos_lexicais" / "catalogo_familias.yaml").read_text(encoding="utf-8")
    )
    desambiguar = {fam for fam, meta in cat.items() if meta.get("desambiguar")}
    assert desambiguar == {"antropomorfica", "militar"}


def test_selecao_de_termos_por_idioma():
    lex = _carregar("_lex_smoke", "04_lexical_coding.py")
    meta = {"termos": ["network"], "termos_pt": ["rede"], "termos_es": ["red"]}
    assert lex.termos_da_familia(meta, "pt") == ["rede"]
    assert lex.termos_da_familia(meta, "es") == ["red"]
    assert lex.termos_da_familia(meta, "en") == ["network"]
    # Recuo para o inglês quando a lista da língua falta.
    assert lex.termos_da_familia({"termos": ["network"]}, "pt") == ["network"]


def test_contagem_respeita_exclusao():
    lex = _carregar("_lex_smoke2", "04_lexical_coding.py")
    padrao = lex.compilar_padroes(["network"])
    exclusao = lex.compilar_padroes(["neural network"])
    assert lex.contar("a neural network here", padrao, exclusao) == 0
    assert lex.contar("a social network here", padrao, exclusao) == 1


def test_reconstrucao_de_abstract_openalex():
    imp = _carregar("_imp_smoke", "01_import_wos.py")
    indice = {"We": [0], "weave": [1], "a": [2], "network": [3]}
    assert imp.reconstruir_abstract(indice) == "We weave a network"
    assert imp.reconstruir_abstract(None) == ""  # dump sem resumo
    assert imp.reconstruir_abstract({}) == ""


def test_normalizacao_de_doi():
    enrich = _carregar("_enrich_smoke", "01c_api_enrich.py")
    assert enrich._norm_doi("https://doi.org/10.1/ABC") == "10.1/abc"
    assert enrich._norm_doi("doi:10.2/x") == "10.2/x"
    assert enrich._norm_doi("10.3/Y") == "10.3/y"
    # NaN, None e vazio não viram DOI espúrio (era o bug do filtro 'nan').
    assert enrich._norm_doi(float("nan")) == ""
    assert enrich._norm_doi(None) == ""
    assert enrich._norm_doi("") == ""
