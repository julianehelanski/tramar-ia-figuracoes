#!/bin/bash
# SessionStart hook: prepara o ambiente Python do projeto nas sessões do Claude
# Code na web, para que o pipeline, o linter e os testes rodem sem setup manual.
set -euo pipefail

# Roda apenas em sessão remota (Claude Code na web). Localmente, não faz nada.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"

VENV="${CLAUDE_PROJECT_DIR:-.}/.venv"
if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV"
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"

python -m pip install --upgrade pip >/dev/null
# Dependências de execução do pipeline (espelho de pyproject [project.dependencies]).
pip install -r requirements.txt
# Ferramentas de desenvolvimento (lint e teste), de pyproject [project.optional-dependencies].
pip install black ruff pytest

# Persiste o venv para o restante da sessão, para que `python`/`pytest`/`ruff`
# resolvam no ambiente do projeto sem reativação manual.
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  {
    echo "export VIRTUAL_ENV=\"$VENV\""
    echo "export PATH=\"$VENV/bin:\$PATH\""
  } >> "$CLAUDE_ENV_FILE"
fi

echo "Ambiente Tramar a IA pronto: requirements.txt + black/ruff/pytest no venv."
