"""Etapa 2, apoio à desambiguação: primeiro passe automático por regras.

Lê os CSV de desambiguação gerados por `04b_desambiguar.py --gerar`
(`outputs/etapa2_codificacao/desambiguacao_<familia>.csv`) e preenche a coluna
`categoria_sugerida` (figurativa | tecnica) por regras de contexto, com uma coluna
`confianca` (alta | baixa) e `motivo` (qual âncora disparou), para reduzir o trabalho
manual: a pesquisadora revisa de perto as de baixa confiança e confere por amostra as
de alta.

Classificação em três vias (a validação mostrou que a binária inflava a figuração
com cognição humana literal das ciências sociais):
- `tecnica`: o contexto traz uma âncora técnica do termo (`attention` perto de
  `mechanism`, `learning` perto de `rate`);
- `figurativa`: o predicado é atribuído à IA (modelo, sistema, algoritmo perto do
  termo); ainda pede conferência entre figurativo e técnico-ML;
- `literal`: o predicado é de humano ou organização (`students learn`, `our
  knowledge`), ou o sujeito é indeterminado.
Só a `figurativa` conta na matriz refinada. A classificação usa só o contexto, nunca
o polo do artigo, para não contaminar o contraste.

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
    # família biológica
    "neural": ["network", "networks", "net", "nets"],
    "evolve": ["evolutionary algorithm", "differential"],
    "evolution": ["evolutionary algorithm", "differential evolution", "computation"],
    "mutation": ["genetic algorithm", "rate", "operator"],
    "growth": ["rate", "curve", "factor"],
    "generation": [
        "text generation",
        "image generation",
        "data generation",
        "code generation",
        "next-generation",
        "generative",
        "retrieval",
    ],
    "cell": ["lstm", "gru", "memory cell", "grid", "unit"],
    "neuron": ["artificial", "spiking"],
    "adapt": ["domain", "adaptive"],
    "adaptation": ["domain", "adaptive"],
    "dna": ["sequencing", "sequence"],
    # família têxtil (network e variantes técnicas)
    "network": [
        "neural",
        "convolutional",
        "deep",
        "recurrent",
        "adversarial",
        "bayesian",
        "architecture",
        "traffic",
        "wireless",
        "sensor",
        "communication",
        "protocol",
        "layer",
        "graph",
        "social",
        "road",
        "transport",
        "complex",
        "attention",
        "backbone",
    ],
    "networks": ["neural", "convolutional", "deep", "adversarial", "bayesian"],
    "mesh": ["network", "wireless", "finite element", "polygon", "3d"],
    "fiber": ["optical", "optic"],
    "fibre": ["optical", "optic"],
    "thread": ["thread-level", "multi-thread", "execution"],
    # família oceânica
    "deep": ["learning", "neural", "network", "reinforcement", "belief", "convolutional"],
    "stream": ["data", "video", "bit", "live", "processing", "input"],
    "streaming": ["data", "video", "live", "media"],
    "flow": [
        "optical",
        "data",
        "work",
        "tensor",
        "traffic",
        "information",
        "gradient",
        "load",
        "normalizing",
    ],
    "flows": ["optical", "data", "traffic", "normalizing"],
    "pipeline": ["data", "processing", "deep", "training", "inference", "ci"],
    "wave": ["wavelet", "waveform", "wave function", "micro", "radio", "electromagnetic"],
    "waves": ["wavelet", "micro", "radio", "electromagnetic"],
    "current": ["electric", "alternating", "direct"],
    "surface": ["decision", "loss", "response", "reconstruction"],
    "depth": ["estimation", "map", "camera", "sensor", "image", "perception", "first"],
    "immersion": ["virtual", "vr"],
    # família extrativa
    "mining": [
        "data",
        "text",
        "process",
        "pattern",
        "opinion",
        "argument",
        "web",
        "graph",
        "frequent",
        "rule",
    ],
    "mine": ["data", "text"],
    "extract": [
        "feature",
        "information",
        "entity",
        "keyword",
        "relation",
        "text",
        "knowledge",
        "data",
        "automatic",
    ],
    "extraction": [
        "feature",
        "information",
        "entity",
        "keyword",
        "relation",
        "text",
        "knowledge",
        "data",
        "automatic",
    ],
    "raw": ["data", "image", "signal", "input", "pixel", "material"],
    "refine": ["mesh", "search", "iteratively", "coarse-to-fine"],
    "refined": ["mesh", "search", "feature"],
    "harvest": ["energy", "data"],
    "harvesting": ["energy", "data"],
    "resource": ["computational", "computing", "allocation", "resource-constrained"],
    "scrape": ["web", "data"],
    "scraping": ["web", "data"],
}


# Sujeitos do predicado, para distinguir figuração da IA de cognição humana literal.
SUJEITO_IA = {
    "model",
    "models",
    "network",
    "networks",
    "system",
    "systems",
    "algorithm",
    "algorithms",
    "ai",
    "machine",
    "machines",
    "robot",
    "robots",
    "llm",
    "llms",
    "gpt",
    "agent",
    "agents",
    "transformer",
    "architecture",
    "software",
    "chatbot",
    "framework",
    "encoder",
    "decoder",
    "classifier",
}
SUJEITO_HUMANO = {
    "student",
    "students",
    "people",
    "person",
    "persons",
    "human",
    "humans",
    "child",
    "children",
    "user",
    "users",
    "researcher",
    "researchers",
    "participant",
    "participants",
    "teacher",
    "teachers",
    "author",
    "authors",
    "society",
    "company",
    "companies",
    "government",
    "team",
    "teams",
    "patient",
    "patients",
    "worker",
    "workers",
    "citizen",
    "citizens",
    "learner",
    "learners",
    "we",
    "our",
    "us",
    "they",
    "their",
    "consumer",
    "consumers",
    "individual",
    "individuals",
    "nurse",
    "doctor",
    "professional",
    "professionals",
    "organization",
    "organisation",
}


def _ctx_limpo(contexto: str) -> str:
    """Contexto KWIC em minúsculas, sem os marcadores [[ ]] do termo central."""
    return re.sub(r"\[\[|\]\]", " ", str(contexto)).lower()


def classificar_sujeito(contexto: str) -> tuple[str | None, int]:
    """Acha o sujeito mais próximo do termo: ('ia'|'humano'|None, distância em palavras).

    Procura para os dois lados do termo (marcado por [[ ]]); o sujeito de menor
    distância vence. None quando nenhum sujeito conhecido aparece na janela.
    """
    partes = re.split(r"\[\[.*?\]\]", str(contexto), maxsplit=1)
    esquerda = re.findall(r"[a-zA-Záàâãéêíóôõúç-]+", partes[0].lower())
    direita = re.findall(r"[a-zA-Záàâãéêíóôõúç-]+", partes[1].lower()) if len(partes) > 1 else []

    melhor_tipo, melhor_dist = None, 999
    for dist, palavra in enumerate(reversed(esquerda), start=1):  # mais perto = antes
        tipo = "ia" if palavra in SUJEITO_IA else ("humano" if palavra in SUJEITO_HUMANO else None)
        if tipo and dist < melhor_dist:
            melhor_tipo, melhor_dist = tipo, dist
            break
    for dist, palavra in enumerate(direita, start=1):
        tipo = "ia" if palavra in SUJEITO_IA else ("humano" if palavra in SUJEITO_HUMANO else None)
        if tipo and dist < melhor_dist:
            melhor_tipo, melhor_dist = tipo, dist
            break
    return melhor_tipo, melhor_dist


# Famílias de metáfora material: a figuração não é predicado de um sujeito, é a
# imagem em si (a trama, a profundidade, a extração). Nelas, o que não é
# técnico-ancorado fica como figuração candidata, não como literal-humano.
FAMILIAS_MATERIAIS = {"biologica", "textil", "oceanica", "extrativa"}


def sugerir(termo: str, contexto: str, familia: str = "") -> tuple[str, str, str]:
    """Devolve (categoria_sugerida, confianca, motivo) em três vias.

    figurativa = a figuração é viva (predicado da IA, nas famílias cognitivas; imagem
                 material sem âncora técnica, nas famílias materiais);
    tecnica    = termo técnico sedimentado (âncora técnica no contexto);
    literal    = predicado de humano ou organização, ou sujeito indeterminado.
    """
    termo_l = str(termo).strip().lower()
    ctx = _ctx_limpo(contexto)
    for ancora in ANCORAS_TEC.get(termo_l, []):
        if ancora in ctx:
            return "tecnica", "alta", f"âncora técnica: {ancora}"

    sujeito, _ = classificar_sujeito(contexto)
    if sujeito == "humano":
        return "literal", "alta", "sujeito humano/organização"

    if str(familia).strip().lower() in FAMILIAS_MATERIAIS:
        return "figurativa", "baixa", "imagem material sem âncora técnica; revisar"

    if sujeito == "ia":
        return "figurativa", "media", "sujeito IA; conferir se é figurativo ou técnico-ML"
    return "literal", "baixa", "sujeito indeterminado; revisar"


def processar(caminho, aceitar_alta: bool, aceitar_tudo: bool, refazer: bool) -> pd.DataFrame:
    """Aplica as regras a um CSV de desambiguação e devolve o DataFrame anotado."""
    df = pd.read_csv(caminho).fillna({"categoria_final": "", "categoria_sugerida": ""})
    sugest = df.apply(lambda r: sugerir(r["termo"], r["contexto"], r.get("familia", "")), axis=1)
    df["categoria_sugerida"] = [s[0] for s in sugest]
    df["confianca"] = [s[1] for s in sugest]
    df["motivo"] = [s[2] for s in sugest]
    if refazer:  # sobrescreve toda a classificação pela sugestão nova
        df["categoria_final"] = df["categoria_sugerida"]
        return df
    vazias = df["categoria_final"].astype(str).str.strip() == ""
    if aceitar_tudo:
        df.loc[vazias, "categoria_final"] = df.loc[vazias, "categoria_sugerida"]
    elif aceitar_alta:
        alvo = vazias & (df["confianca"] == "alta")
        df.loc[alvo, "categoria_final"] = df.loc[alvo, "categoria_sugerida"]
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--aceitar-alta",
        action="store_true",
        help="preenche categoria_final nas de alta confiança (técnicas)",
    )
    parser.add_argument(
        "--aceitar-tudo",
        action="store_true",
        help="preenche categoria_final por toda a sugestão (versão rápida a corrigir por amostra)",
    )
    parser.add_argument(
        "--refazer",
        action="store_true",
        help="sobrescreve categoria_final inteira pela sugestão nova (reaplica a regra)",
    )
    args = parser.parse_args()

    csvs = sorted(ETAPA2.glob("desambiguacao_*.csv"))
    if not csvs:
        raise SystemExit(
            "Nenhum desambiguacao_*.csv em outputs/etapa2_codificacao/. "
            "Rode antes: python scripts/04b_desambiguar.py --gerar"
        )

    for caminho in csvs:
        df = processar(caminho, args.aceitar_alta, args.aceitar_tudo, args.refazer)
        df.to_csv(caminho, index=False)
        familia = caminho.stem.replace("desambiguacao_", "")
        n = len(df)
        cont = df["categoria_sugerida"].value_counts()
        preenchidas = int((df["categoria_final"].astype(str).str.strip() != "").sum())
        print(f"\n=== {familia}: {n} ocorrências ===")
        for cat in ("figurativa", "tecnica", "literal"):
            q = int(cont.get(cat, 0))
            print(f"  {cat}: {q} ({q / n:.0%})")
        print(f"  categoria_final já preenchida: {preenchidas}")
        amostra = df[df["categoria_sugerida"] == "figurativa"].head(4)
        if not amostra.empty:
            print("  amostra de figurativa (sujeito IA; conferir figurativo vs técnico-ML):")
            for _, r in amostra.iterrows():
                print(f"    [{r['termo']}] {str(r['contexto'])[:90]}")

    print(
        "\nConfira as figurativas (sujeito IA) e as de baixa confiança, ajuste "
        "categoria_final, e rode: python scripts/04b_desambiguar.py"
    )


if __name__ == "__main__":
    main()
