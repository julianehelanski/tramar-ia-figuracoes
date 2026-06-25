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

## 2026-06-24 (decisões 2.a e 2.d resolvidas)

- Decisão 2.a, anais de conferência: resolvida pela opção (i), incluir anais
  indexados com revisão por pares. `Proceedings Paper` permanece na *query* e em
  `03_apply_criteria.py`. arXiv fica como complemento condicionado à busca-piloto.
- Decisão 2.d, amostragem do subcorpus: resolvida pela amostragem teórica por
  densidade figurativa, estratificada por período e estrato disciplinar, com
  citação como descritor secundário. Operacionalizada em
  `scripts/08_sample_subcorpus.py` (seed=42), testada sobre exportação sintética.
- Detalhe das duas em `docs/decisoes_metodologicas.md` (seções 2.a, 2.d e 6).
- Dependência aberta registrada: definição operacional do polo técnico contra o
  crítico, que entrará como estrato adicional na amostragem quando fixada.

## 2026-06-24 (decisões 2.b e 2.c resolvidas)

- Decisão 2.b, estratégia de query: resolvida pela híbrida faseada. Começo pela
  restritiva (query v1) com busca-piloto de dimensionamento; a ampla entra depois,
  com amostragem, condicionada ao volume.
- Decisão 2.c, bases: WoS e Scopus na Etapa 1 (o pipeline já deduplica por DOI);
  arXiv condicionado ao gatilho da 2.a.
- Decisão 2.c, idioma: inglês, português e espanhol desde a Etapa 1.
- Consequência operacional: catálogo estendido com `termos_pt`/`termos_es` e
  exclusões por língua; `04_lexical_coding.py` e `04b_desambiguar.py` passaram a
  escolher a lista pela coluna `idioma`, com recuo para o inglês. Mecanismo testado
  sobre exportação sintética pt/es.
- Pendência registrada: as listas pt/es são rascunho v0 a validar por Juliane antes
  de codificar corpus dessas línguas. Refinações anotadas: normalização de acentos
  e tratamento de flexões/plurais (decisões de calibração, seção 7 das decisões).

## 2026-06-24 (automação de ambiente)

- Hook de SessionStart em `.claude/hooks/session-start.sh`, registrado em
  `.claude/settings.json`, para as sessões do Claude Code na web subirem com o
  ambiente pronto: cria o venv, instala `requirements.txt` e as ferramentas de
  desenvolvimento (black, ruff, pytest), e persiste o venv na sessão. Roda só em
  sessão remota (`CLAUDE_CODE_REMOTE`), em modo síncrono.
- Suíte de fumaça em `tests/` (catálogo com nove famílias, famílias a desambiguar,
  seleção de termos por idioma, exclusão na contagem). Quatro testes, passando.
- Lint do repositório alinhado a ruff e black (linha 100, config em pyproject):
  imports reordenados, `zip(strict=True)` e ajustes menores. Pipeline revalidado de
  ponta a ponta após a formatação.

## 2026-06-24 (protocolo de extração)

- Protocolo de extração das bases em `docs/protocolo_extracao.md`: passo a passo de
  exportação na WoS (tab-delimited, Full Record, lotes de 1000) e na Scopus (CSV
  com os três grupos de campos, lotes de ~2000), formatos que o `01_import_wos.py`
  consome, mais a conferência amostral pós-importação.
- Query Scopus v1 em `corpus/queries/scopus_query_v1.txt`, tradução da WoS v1 para a
  sintaxe TITLE-ABS-KEY/DOCTYPE/LANGUAGE (decisão 2.c trouxe a Scopus ao escopo).
- Referências de PRISMA apontadas ao arquivo real `docs/prisma/fluxograma_prisma.md`.

## 2026-06-24 (enriquecimento híbrido por API)

- Decisão 2.c híbrida operacionalizada: o resumo vem do export manual, e os
  metadados de citação e área vêm por DOI de API aberta. Script
  `scripts/01c_api_enrich.py` (OpenAlex padrão, Crossref alternativo) acrescenta
  `citacoes_openalex`, `area_openalex`, `tipo_openalex` sem sobrescrever campos
  nativos. `requests` adicionado a `requirements.txt`; alvo `make enrich`.
- Limitação de ambiente registrada: a política de rede do contêiner do Claude Code
  nega a saída para essas APIs (OpenAlex devolveu 403 no proxy de egresso), então o
  enriquecimento roda na máquina da Juliane, não no ambiente remoto. O VPN da
  Unicamp vale para a máquina dela, não para o contêiner.
- Sobre a API paga: depende de chave e de licença de API na assinatura (a confirmar
  com a biblioteca); a Starter API da WoS não traz resumo e a Search da Scopus só
  traz resumo na visão COMPLETE, o que sustenta manter o resumo no export manual.

## 2026-06-25 (leitor OpenAlex)

- `01_import_wos.py` ganhou `--base openalex`: lê dump da OpenAlex em JSON (lista de
  works ou página da API) ou JSONL, mapeia ao esquema e **reconstrói o resumo** a
  partir de `abstract_inverted_index` quando presente. Sem o índice, o resumo fica
  vazio e a análise roda na versão limitada. O campo do tópico primário entra em
  `categoria_wos` como estrato disciplinar. Testado em JSON e JSONL, com e sem
  resumo; teste de reconstrução em `tests/`.
- Protocolo de extração atualizado (seção 2b) com o passo OpenAlex e a recomendação
  de pedir `abstract_inverted_index` no `select` da API.

## 2026-06-25 (primeira análise plena e visualizações)

- Amostra estratificada global da OpenAlex (5.000 técnico, 5.000 crítico, `seed=42`,
  resumos reconstruídos), rodada de ponta a ponta. Após dedup e critérios, 6.296
  artigos codificados.
- Desambiguação por passe automático (`04c`, com `--aceitar-alta` e `--aceitar-tudo`)
  e validação por amostra (`04d`). Antropomórfica 4.472 → 3.419 figurativas; militar
  1.638 → 1.243.
- Contraste técnico contra crítico (`09`) e figuras de leitura: barras (`10`), redes
  de co-ocorrência por polo (`11`), radar (`12`). Achado central: antropomórfica
  cerca de 73 (crítico) contra 38 (técnico) por 100 artigos, contraste que se acentua
  com a desambiguação.
- README didático do processo em `docs/passo_a_passo_analise.md`, com os termos do
  catálogo, para uso em apresentação. Decisão registrada na seção 8 das decisões.

## Expansões do catálogo

Registrar aqui cada termo ou família acrescentado durante a codificação, com data
e motivo, mantendo o catálogo auditável.

| Data | Família | Termo(s) acrescentado(s) | Motivo |
| :--- | :--- | :--- | :--- |
|      |         |                          |        |
