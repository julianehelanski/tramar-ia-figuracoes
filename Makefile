# Tramar a IA: atalhos do pipeline.
# Uso: make setup; depois make all (ou alvos individuais).
# Importação (01) depende de fontes escolhidas; ver `make import FONTES=...`.

PY := python
VENV := .venv

.PHONY: help setup import dedup criteria coding refine-gen refine distribution topics all clean

help:
	@echo "Alvos:"
	@echo "  setup        cria .venv e instala requirements.txt"
	@echo "  import       importa exportações: make import FONTES='wos.txt:wos scopus.csv:scopus'"
	@echo "  dedup        02_dedup.py"
	@echo "  criteria     03_apply_criteria.py"
	@echo "  coding       04_lexical_coding.py (contagem bruta)"
	@echo "  refine-gen   04b_desambiguar.py --gerar (CSV em branco para classificar)"
	@echo "  refine       04b_desambiguar.py (aplica os CSV já classificados)"
	@echo "  distribution 05_cooccurrence.py e 06_distribution.py"
	@echo "  topics       07_topic_model.py (LDA; N=make topics N=15)"
	@echo "  all          dedup -> criteria -> coding -> distribution"

setup:
	$(PY) -m venv $(VENV)
	. $(VENV)/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	@echo "Ative com: source $(VENV)/bin/activate"

import:
	$(PY) scripts/run_all.py --importar $(FONTES)

dedup:
	$(PY) scripts/02_dedup.py

criteria:
	$(PY) scripts/03_apply_criteria.py

coding:
	$(PY) scripts/04_lexical_coding.py

refine-gen:
	$(PY) scripts/04b_desambiguar.py --gerar

refine:
	$(PY) scripts/04b_desambiguar.py

distribution:
	$(PY) scripts/05_cooccurrence.py
	$(PY) scripts/06_distribution.py

N ?= 15
topics:
	$(PY) scripts/07_topic_model.py --metodo lda --n-topicos $(N)

all:
	$(PY) scripts/run_all.py

clean:
	rm -rf outputs/etapa2_codificacao/codificacao_lexical*.csv \
	       outputs/etapa3_distribuicao/* outputs/figuras/*.png
	@echo "Saídas derivadas removidas (metadata e CSV de desambiguação preservados)."
