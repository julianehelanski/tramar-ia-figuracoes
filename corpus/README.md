# Corpus

Esta pasta organiza a constituição do corpus (Etapa 1).

## Subpastas

- `queries/`: *queries* de busca versionadas (uma por base e versão). Texto puro,
  com cabeçalho de data e notas de calibração. Versionado.
- `exports/`: exportações brutas das bases (WoS, Scopus), nos formatos nativos
  (RIS, BibTeX, *tab-delimited*). **Não versionado** (grande e mutável); manter
  cópia local ou no Drive. Ver `.env.example` para apontar um caminho externo.
- `metadata/`: metadados consolidados do corpus após importação e deduplicação
  (`corpus_metadata.csv`). Versionado: é a fonte da verdade do corpus.
- `txt/`: texto integral dos artigos (PDF ou txt extraído). **Não versionado**
  (copyright). Fica em pasta local apontada por `CORPUS_FULLTEXT_PATH` no `.env`.

## Esquema de `corpus_metadata.csv`

Colunas mínimas para o pipeline:

| Coluna | Descrição |
| :--- | :--- |
| `id` | identificador interno estável do artigo |
| `doi` | DOI normalizado (chave primária de deduplicação) |
| `titulo` | título |
| `autores` | autores |
| `ano` | ano de publicação |
| `fonte` | periódico ou anais |
| `base` | base de origem (wos, scopus, arxiv) |
| `categoria_wos` | categoria(s) WoS, para estratificação disciplinar |
| `tipo_doc` | Article, Review, Proceedings Paper |
| `idioma` | en, pt, es |
| `citacoes` | contagem de citações (para amostragem por citação) |
| `abstract` | resumo (base da codificação lexical sem texto integral) |
| `incluido` | bool, resultado da aplicação dos critérios (Etapa 1) |
| `motivo_exclusao` | preenchido quando `incluido` é falso |
| `no_subcorpus` | bool, marcado na seleção para leitura próxima (Etapa 4) |
