"""Orquestrador do pipeline: encadeia os passos da Etapa 1 à Etapa 3.

Roda os scripts numerados em ordem, como subprocessos, sobre o mesmo interpretador
Python. A importação (passo 01) depende de fontes escolhidas por Juliane, então só
roda quando `--importar` é passado; sem ele, o orquestrador assume que
`corpus/metadata/corpus_metadata.csv` já existe.

A desambiguação manual (passo 04b) não é totalmente automatizável: a geração dos
CSV (`--gerar`) e a classificação são manuais. Com `--desambiguar`, o orquestrador
aplica os CSV já classificados antes da distribuição; os passos 05 e 06 então leem
a matriz refinada.

Uso:
    python scripts/run_all.py                          # 02..06 sobre metadata
    python scripts/run_all.py --importar wos.txt:wos scopus.csv:scopus
    python scripts/run_all.py --desambiguar            # inclui 04b (aplicar)
    python scripts/run_all.py --topicos 15             # inclui 07 (LDA)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def rodar(script: str, *args: str) -> None:
    """Executa um script do pipeline como subprocesso; aborta no primeiro erro."""
    cmd = [sys.executable, str(SCRIPTS / script), *args]
    print(f"\n=== {script} {' '.join(args)} ===", flush=True)
    resultado = subprocess.run(cmd, cwd=SCRIPTS)
    if resultado.returncode != 0:
        raise SystemExit(f"Falha em {script} (código {resultado.returncode}).")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--importar", nargs="+", metavar="FONTE:BASE", default=None,
                        help="pares fonte:base para o passo 01 (ex.: wos.txt:wos)")
    parser.add_argument("--desambiguar", action="store_true",
                        help="aplicar a desambiguação manual (04b) antes de 05/06")
    parser.add_argument("--topicos", type=int, metavar="N", default=None,
                        help="rodar topic modeling LDA (07) com N tópicos")
    parser.add_argument("--subcorpus", type=int, metavar="N", default=None,
                        help="selecionar subcorpus de leitura (08) com N artigos")
    args = parser.parse_args()

    if args.importar:
        fontes: list[str] = []
        for par in args.importar:
            if ":" not in par:
                parser.error(f"esperado FONTE:BASE, recebido {par!r}")
            fonte, base = par.rsplit(":", 1)
            fontes += ["--fonte", fonte, "--base", base]
        rodar("01_import_wos.py", *fontes)

    rodar("02_dedup.py")
    rodar("03_apply_criteria.py")
    rodar("04_lexical_coding.py")
    if args.desambiguar:
        rodar("04b_desambiguar.py")
    rodar("05_cooccurrence.py")
    rodar("06_distribution.py")
    if args.topicos is not None:
        rodar("07_topic_model.py", "--metodo", "lda", "--n-topicos", str(args.topicos))
    if args.subcorpus is not None:
        rodar("08_sample_subcorpus.py", "--alvo", str(args.subcorpus))

    print("\nPipeline concluído. Saídas em outputs/. Registre as contagens PRISMA "
          "em docs/prisma/fluxograma_prisma.md.")


if __name__ == "__main__":
    main()
