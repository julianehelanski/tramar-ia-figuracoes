# Histórico

Índice cronológico de decisões, documentos consumidos e expansões do catálogo.

## 2026-06-24

- Repositório criado a partir do roteiro de pesquisa *Tramar a inteligência
  artificial* (versão 1.0, maio de 2026).
- Estrutura inicial montada espelhando convenções de `analise-figuracoes-latour`.
- Catálogo de nove famílias semânticas transposto da seção 4.2 do roteiro
  (`campos_lexicais/catalogo_familias.yaml`).
- *Query* WoS v1 (restritiva refinada) versionada em
  `corpus/queries/wos_query_v1.txt`.
- Decisões registradas em `docs/decisoes_metodologicas.md`: desenho de artigo
  autônomo (seção 1), pendências sobre anais, estratégia de query, bases/idioma e
  amostragem por citação (seção 2), desambiguação das famílias antropomórfica e
  militar (seção 3), seed fixo e PRISMA/ENTREQ (seção 5).

## 2026-06-24 (implementação do pipeline)

- Pipeline Python implementado e testado de ponta a ponta sobre exportação
  sintética (não versionada): importação, deduplicação, critérios, codificação
  lexical, desambiguação, co-ocorrência e distribuição rodam encadeados.
- `01_import_wos.py`: parsing de WoS *tab-delimited*, Scopus CSV e RIS, com
  normalização de DOI (chave de deduplicação, *case-insensitive*) e de idioma para
  códigos ISO. Aceita múltiplas fontes numa execução.
- `04_lexical_coding.py`: passou a honrar o campo `exclusoes` do catálogo, numa
  janela de 5 palavras de cada lado (remove, por exemplo, `network` precedido de
  `neural`). Sem isso a contagem têxtil e oceânica vinha inflada.
- `04b_desambiguar.py`: novo passo no molde war/wars (decisão 3). `--gerar`
  escreve um CSV de ocorrências com contexto KWIC (janela de 8 palavras) e coluna
  `categoria_final` em branco; `--aplicar` lê a classificação manual e gera
  `codificacao_lexical_refinada.csv` contando apenas as ocorrências `figurativa`.
- `_paths.matriz_lexical_path()`: os passos 05 e 06 leem a matriz refinada quando
  ela existe, senão a bruta.
- `07_topic_model.py`: LDA com gensim implementado, seed fixo (`SEED=42`),
  tokenização leve com *stopwords* en/pt/es (lematização spaCy fica como
  refinamento posterior).
- Orquestração: `scripts/run_all.py` e `Makefile` encadeiam os passos.
- Observação para Juliane: o catálogo casa formas exatas, então plurais e flexões
  (`deploys`, `targets`, `weapons`) não são capturados pelos termos no singular.
  Decidir, na calibração, se acrescento variantes flexionadas ao catálogo ou se
  introduzo lematização antes da contagem.

## Expansões do catálogo

Registrar aqui cada termo ou família acrescentado durante a codificação, com data
e motivo, mantendo o catálogo auditável.

| Data | Família | Termo(s) acrescentado(s) | Motivo |
| :--- | :--- | :--- | :--- |
|      |         |                          |        |
