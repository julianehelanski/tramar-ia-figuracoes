"""Etapa 2, apoio à desambiguação: primeiro passe automático por regras.

Lê os CSV de desambiguação gerados por `04b_desambiguar.py --gerar`
(`outputs/etapa2_codificacao/desambiguacao_<familia>.csv`) e preenche a coluna
`categoria_sugerida` (figurativa | tecnica) por regras de contexto, com uma coluna
`confianca` (alta | baixa) e `motivo` (qual âncora disparou), para reduzir o trabalho
manual: a pesquisadora revisa de perto as de baixa confiança e confere por amostra as
de alta.

A regra é transparente e conservadora: se o contexto KWIC traz uma âncora técnica do
termo (por exemplo, `attention` perto de `mechanism`, `learning` perto de `rate`),
sugere `tecnica` com confiança alta; senão, sugere `figurativa` com confiança baixa,
para revisão. A classificação usa só o contexto, nunca o polo do artigo, para não
contaminar o contraste técnico contra crítico.

Com `--aceitar-alta`, copia a sugestão para `categoria_final` apenas nas de alta
confiança (as técnicas ancoradas), deixando as de baixa confiança em branco para a
revisão manual. Nunca sobrescreve `categoria_final` já preenchida.

Uso:
    python scripts/04c_sugerir_desambiguacao.py
    python scripts/04c_sugerir_desambiguacao.py --aceitar-alta
"""

from __future__ import annotations

import argparse
import re

import pandas as pd
from _paths import ETAPA2

# Âncoras técnicas por termo (radical em minúsculas -> expressões que, no contexto,
# indicam uso técnico-literal). Conservador: na dúvida, deixa para revisão manual.
ANCORAS_TEC: dict[str, list[str]] = {
    # família antropomórfica
    "attention": [
        "mechanism",
        "head",
        "self-attention",
        "self attention",
        "multi-head",
        "layer",
        "weights",
        "map",
        "score",
        "transformer",
    ],
    "memory": [
        "module",
        "lstm",
        "gru",
        "cell",
        "buffer",
        "footprint",
        "bank",
        "working memory",
        "external memory",
        "ram",
        "usage",
        "requirement",
    ],
    "learning": [
        "machine",
        "deep",
        "supervised",
        "unsupervised",
        "reinforcement",
        "self-supervised",
        "transfer",
        "federated",
        "rate",
        "curve",
        "representation",
        "feature",
        "contrastive",
        "active",
        "online",
        "ensemble",
        "metric",
        "meta-learning",
        "curriculum",
    ],
    "learn": ["machine", "deep", "supervised", "reinforcement", "rate"],
    "intelligence": ["artificial", "computational", "swarm", "ambient", "business", "collective"],
    "intelligent": ["artificial", "computational", "swarm", "ambient"],
    "agent": [
        "reinforcement",
        "multi-agent",
        "multi agent",
        "autonomous",
        "software",
        "conversational",
        "embodied",
        "based",
    ],
    "agentic": ["reinforcement", "autonomous"],
    "reasoning": [
        "chain-of-thought",
        "chain of thought",
        "symbolic",
        "logical",
        "automated",
        "commonsense",
        "probabilistic",
        "case-based",
    ],
    "reason": ["symbolic", "logical", "automated"],
    "decision": ["tree", "making", "support", "boundary", "theoretic", "fusion"],
    "decide": ["boundary"],
    "perception": ["computer", "machine", "remote", "depth"],
    "perceive": ["computer", "machine"],
    "knowledge": [
        "base",
        "graph",
        "distillation",
        "representation",
        "transfer",
        "prior",
        "domain",
        "extraction",
    ],
    "understanding": [
        "natural language",
        "scene",
        "image",
        "video",
        "semantic",
        "reading",
        "spoken",
    ],
    "understand": ["natural language", "scene", "semantic"],
    "belief": ["propagation", "network", "state", "bayesian", "function"],
    "believe": ["propagation", "bayesian"],
    "aware": ["context", "situation", "situational", "energy", "context-aware"],
    "awareness": ["context", "situation", "situational"],
    "hallucination": ["model", "factual", "mitigate", "object", "llm"],
    "hallucinate": ["model", "factual"],
    "creative": ["computational"],
    "creativity": ["computational"],
    "thinking": ["design", "system", "systems"],
    # família militar
    "deploy": [
        "model",
        "system",
        "software",
        "production",
        "cloud",
        "edge",
        "application",
        "service",
        "real-world",
        "sensor",
    ],
    "deployment": ["model", "system", "software", "production", "cloud", "edge"],
    "target": [
        "variable",
        "class",
        "label",
        "domain",
        "function",
        "value",
        "output",
        "detection",
        "tracking",
        "molecule",
        "gene",
        "protein",
        "drug",
    ],
    "targeting": ["detection", "tracking"],
    "attack": [
        "adversarial",
        "cyber",
        "injection",
        "poisoning",
        "backdoor",
        "evasion",
        "perturbation",
        "robustness",
        "ddos",
        "gradient",
        "white-box",
        "black-box",
    ],
    "adversarial": [
        "example",
        "training",
        "perturbation",
        "robustness",
        "network",
        "attack",
        "loss",
    ],
    "defense": ["adversarial", "cyber", "mechanism", "robust"],
    "defence": ["adversarial", "cyber", "robust"],
    "strategy": [
        "search",
        "sampling",
        "optimization",
        "gradient",
        "learning",
        "exploration",
        "training",
        "selection",
    ],
    "strategic": ["search", "optimization"],
    "operation": [
        "convolution",
        "matrix",
        "tensor",
        "arithmetic",
        "research",
        "point-wise",
        "element-wise",
        "floating",
    ],
    "command": ["voice", "control", "line", "prompt", "and control"],
    "surveillance": ["video", "camera", "visual"],
    "threat": ["model", "detection", "cyber", "intelligence"],
    "campaign": ["marketing", "advertising", "email", "social media"],
    "frontier": ["model", "models", "efficient"],
    "weapon": ["autonomous", "lethal", "nuclear"],
    "weaponize": ["autonomous", "lethal"],
}


def _ctx_limpo(contexto: str) -> str:
    """Contexto KWIC em minúsculas, sem os marcadores [[ ]] do termo central."""
    return re.sub(r"\[\[|\]\]", " ", str(contexto)).lower()


def sugerir(termo: str, contexto: str) -> tuple[str, str, str]:
    """Devolve (categoria_sugerida, confianca, motivo) por âncora de contexto."""
    termo_l = str(termo).strip().lower()
    ancoras = ANCORAS_TEC.get(termo_l, [])
    ctx = _ctx_limpo(contexto)
    for ancora in ancoras:
        if ancora in ctx:
            return "tecnica", "alta", f"âncora técnica: {ancora}"
    return "figurativa", "baixa", "sem âncora técnica; revisar"


def processar(caminho, aceitar_alta: bool) -> pd.DataFrame:
    """Aplica as regras a um CSV de desambiguação e devolve o DataFrame anotado."""
    df = pd.read_csv(caminho).fillna({"categoria_final": "", "categoria_sugerida": ""})
    sugest = df.apply(lambda r: sugerir(r["termo"], r["contexto"]), axis=1)
    df["categoria_sugerida"] = [s[0] for s in sugest]
    df["confianca"] = [s[1] for s in sugest]
    df["motivo"] = [s[2] for s in sugest]
    if aceitar_alta:
        vazias_alta = (df["categoria_final"].astype(str).str.strip() == "") & (
            df["confianca"] == "alta"
        )
        df.loc[vazias_alta, "categoria_final"] = df.loc[vazias_alta, "categoria_sugerida"]
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--aceitar-alta",
        action="store_true",
        help="preenche categoria_final nas de alta confiança (técnicas)",
    )
    args = parser.parse_args()

    csvs = sorted(ETAPA2.glob("desambiguacao_*.csv"))
    if not csvs:
        raise SystemExit(
            "Nenhum desambiguacao_*.csv em outputs/etapa2_codificacao/. "
            "Rode antes: python scripts/04b_desambiguar.py --gerar"
        )

    for caminho in csvs:
        df = processar(caminho, args.aceitar_alta)
        df.to_csv(caminho, index=False)
        familia = caminho.stem.replace("desambiguacao_", "")
        n = len(df)
        n_alta = int((df["confianca"] == "alta").sum())
        n_fig = int((df["categoria_sugerida"] == "figurativa").sum())
        preenchidas = int((df["categoria_final"].astype(str).str.strip() != "").sum())
        print(f"\n=== {familia}: {n} ocorrências ===")
        print(f"  técnica ancorada (alta confiança): {n_alta}  " f"({n_alta / n:.0%})")
        print(f"  figurativa sugerida (baixa, revisar): {n_fig}")
        print(f"  categoria_final já preenchida: {preenchidas}")
        amostra = df[df["confianca"] == "baixa"].head(4)
        if not amostra.empty:
            print("  amostra para revisão (baixa confiança):")
            for _, r in amostra.iterrows():
                print(f"    [{r['termo']}] {str(r['contexto'])[:90]}")

    print(
        "\nRevise as de baixa confiança nos CSV (coluna categoria_final), confira por "
        "amostra as de alta, e rode: python scripts/04b_desambiguar.py"
    )


if __name__ == "__main__":
    main()
