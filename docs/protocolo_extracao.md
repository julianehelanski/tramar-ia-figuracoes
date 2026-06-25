# Protocolo de extração de dados das bases

Passo a passo para exportar o corpus da Web of Science e da Scopus nos formatos que
o pipeline consome (`scripts/01_import_wos.py`). Procedimento técnico, com listas e
comandos. As decisões metodológicas por trás dele ficam em
`docs/decisoes_metodologicas.md` (seção 2).

A ordem de trabalho é sempre: busca-piloto, calibração, busca definitiva,
exportação em lotes, importação, deduplicação, critérios.

---

## 0. Antes de começar

1. **Acesso institucional.** WoS e Scopus exigem assinatura. Pela Unicamp, acessar
   por dentro da rede (VPN) ou pelo acesso federado CAFe/CRUESP, que valida o login
   nas duas plataformas.
2. **Pasta de exportações.** Os arquivos brutos não entram no repositório (são
   grandes e mutáveis). Definir onde eles ficam:
   - opção simples: salvar em `corpus/exports/` (já ignorada pelo git);
   - opção Drive: apontar `CORPUS_EXPORTS_PATH` no `.env` para uma pasta
     sincronizada (ver `.env.example`). O `01_import_wos.py` procura os arquivos no
     caminho dado e, se não achar, em `CORPUS_EXPORTS_PATH`.
3. **Data da busca.** Anotar a data de cada busca. As bases atualizam o índice, e a
   contagem muda com o tempo; o PRISMA exige a data.
4. **Busca-piloto primeiro.** Seguir o protocolo de piloto no fim de
   `corpus/queries/wos_query_v1.txt` antes da busca definitiva: rodar a restritiva,
   registrar o total, ler os 20 primeiros, calibrar termos, anotar em
   `docs/prisma/fluxograma_prisma.md`.

---

## 1. Web of Science

1. Entrar em `webofscience.com` com o login institucional.
2. No alto, escolher a coleção **Web of Science Core Collection**.
3. Abrir **Advanced Search** (Pesquisa Avançada).
4. Colar a query de `corpus/queries/wos_query_v1.txt` (o bloco entre as linhas
   tracejadas) e rodar.
5. Conferir o **total de registros** e registrar em
   `docs/prisma/fluxograma_prisma.md`, com a data.
6. Abrir o conjunto de resultados e clicar em **Export** -> **Tab delimited file**.
7. Em **Record Content**, escolher **Full Record**. Isso garante o resumo (AB), as
   categorias WoS (WC), o tipo (DT), o idioma (LA) e as citações (TC), que o
   pipeline mapeia.
8. **Intervalo de registros**: a WoS exporta no máximo **1000 registros por
   arquivo**. Para corpora maiores, exportar em lotes: 1 a 1000, 1001 a 2000, e
   assim por diante.
9. Salvar cada lote em `corpus/exports/` com nome estável, por exemplo
   `wos_2026-06_lote1.txt`, `wos_2026-06_lote2.txt`.

Formato: texto *tab-delimited*, codificação UTF-8 (o leitor usa `utf-8-sig`, então
o BOM da WoS não atrapalha).

Importar (um par `--fonte ... --base wos` por lote):

```bash
python scripts/01_import_wos.py \
    --fonte corpus/exports/wos_2026-06_lote1.txt --base wos \
    --fonte corpus/exports/wos_2026-06_lote2.txt --base wos
```

---

## 2. Scopus

1. Entrar em `scopus.com` com o login institucional.
2. Abrir **Advanced search** (Pesquisa Avançada).
3. Colar a query de `corpus/queries/scopus_query_v1.txt` (o bloco entre as linhas
   tracejadas) e rodar.
4. Conferir o **total** e registrar em `docs/prisma/fluxograma_prisma.md`.
5. Selecionar todos os documentos e clicar em **Export** -> **CSV**.
6. Em **Select the information to export**, marcar os grupos que cobrem as colunas
   do esquema:
   - **Citation information**: autores, título, ano, fonte (Source title), tipo de
     documento, contagem de citações;
   - **Bibliographical information**: DOI e idioma (Language of Original Document);
   - **Abstract & keywords**: resumo (Abstract).
   Sem esses três grupos, faltam colunas que o pipeline espera (sobretudo DOI,
   idioma e resumo).
7. **Limite por exportação**: com resumo incluído, a Scopus limita a cerca de
   **2000 registros por arquivo**. Exportar em lotes se passar disso.
8. Salvar cada lote em `corpus/exports/`, por exemplo `scopus_2026-06_lote1.csv`.

Importar:

```bash
python scripts/01_import_wos.py \
    --fonte corpus/exports/scopus_2026-06_lote1.csv --base scopus
```

WoS e Scopus podem ser importadas na mesma execução, repetindo os pares:

```bash
python scripts/01_import_wos.py \
    --fonte corpus/exports/wos_2026-06_lote1.txt --base wos \
    --fonte corpus/exports/scopus_2026-06_lote1.csv --base scopus
```

---

## 3. Alternativa: formato RIS

As duas bases também exportam **RIS**, que o pipeline lê com `--base ris` (exige
`rispy`, já em `requirements.txt`). Útil quando o *tab-delimited* ou o CSV vier com
quebras de campo. O RIS carrega menos campos (sem categoria WoS, sem contagem de
citações), então prefira *tab-delimited* (WoS) e CSV (Scopus) como padrão.

---

## 4. Depois de importar

1. Rodar a deduplicação e os critérios:
   ```bash
   python scripts/02_dedup.py
   python scripts/03_apply_criteria.py
   ```
   ou tudo de uma vez a partir dos lotes:
   ```bash
   python scripts/run_all.py \
       --importar wos_2026-06_lote1.txt:wos scopus_2026-06_lote1.csv:scopus
   ```
2. Registrar em `docs/prisma/fluxograma_prisma.md`, a cada etapa: total bruto por
   base, duplicatas removidas, incluídos e excluídos por critério. É o que alimenta
   o fluxograma PRISMA.
3. **Conferência amostral** de `corpus/metadata/corpus_metadata.csv`:
   - `abstract` não vazio na maioria dos registros (a codificação lexical depende
     dele; registros sem resumo entram com contagem zero);
   - `idioma` mapeado para `en`/`pt`/`es` (valores vazios indicam rótulo de base
     fora do mapa em `01_import_wos.py`, a estender se aparecer);
   - `doi` presente onde possível (chave de deduplicação; sem DOI, a dedup recai no
     título normalizado).

---

## 4b. Enriquecimento por DOI via API aberta (híbrido)

Decisão 2.c híbrida: o resumo vem da exportação manual, e os metadados de citação e
área disciplinar são enriquecidos por DOI através de uma API acadêmica aberta, sem
chave, sem licença de WoS/Scopus e sem IP institucional. Isso resolve o ponto da
Scopus não trazer categoria WoS e atualiza as citações para uma contagem com data
única em todo o corpus.

Passo, na sua máquina (o ambiente remoto do Claude Code não alcança essas APIs, a
política de rede do contêiner nega a saída):

```bash
python scripts/01c_api_enrich.py --email voce@unicamp.br
# ou, alternativa: --provedor crossref
```

O script lê os DOIs de `corpus_metadata.csv`, consulta a OpenAlex em lotes de 50, e
acrescenta as colunas `citacoes_openalex`, `area_openalex` e `tipo_openalex`, sem
tocar no `abstract` nem nos campos nativos das bases. Registros sem DOI ficam em
branco nessas colunas. A `area_openalex` serve de estrato disciplinar na Etapa 3,
útil sobretudo para os registros Scopus, que vêm sem categoria WoS.

Sobre a API paga das bases: WoS e Scopus têm API, mas o acesso depende de chave e de
a assinatura da Unicamp incluir licença de API (em geral contrato à parte do acesso
web), a confirmar com a biblioteca. Mesmo com chave, a Starter API da WoS não traz
resumo, e a Search API da Scopus só traz resumo na visão `COMPLETE`. Por isso o
resumo continua vindo do export manual, e a API entra só no enriquecimento.

## 5. Reexecução e versionamento

- Os arquivos de `corpus/exports/` não são versionados. Guardar uma cópia no Drive
  com a data, para reproduzir a constituição do corpus.
- O `corpus/metadata/corpus_metadata.csv` consolidado é versionado: é a fonte da
  verdade do corpus. Commitar quando a importação estabilizar.
- Refazer a busca em data posterior gera contagens diferentes; tratar como nova
  versão da query (v2) e registrar no histórico.
