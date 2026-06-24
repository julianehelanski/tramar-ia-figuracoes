# Tramar a inteligência artificial

Análise textual sistemática das figurações e tropos mobilizados em artigos
científicos sobre inteligência artificial. O projeto articula duas escalas: uma
bibliométrica, que constitui o corpus por critérios sistemáticos de busca e
inclusão em bases indexadas, e uma interpretativa-figurativa, que lê de perto o
que as metáforas fazem no texto científico, em diálogo com a tradição que vai de
Lakoff e Johnson sobre metáforas conceituais até Haraway sobre figurações como
entidades material-semióticas.

O projeto integra o programa de pesquisa sobre o Centro de Inteligência
Artificial (C4AI) da USP e pode operar como artigo autônomo ou como apêndice
metodológico de um documento mais amplo. Esta versão do repositório assume o
desenho de artigo autônomo.

## Pergunta de pesquisa

A literatura sobre IA opera em registros figurativos heterogêneos. A hipótese é
que a diferença figurativa entre a literatura técnica e a crítica funciona como
indício empírico das partições disciplinares que organizam o campo. A figuração
têxtil, desenvolvida em outros trabalhos da autora, entra aqui como hipótese a
ser testada empiricamente sobre o material, não como expectativa a confirmar.

## Desenho metodológico

A metodologia segue quatro etapas interdependentes, cada uma com sua pasta de
saídas em `outputs/`.

1. **Constituição do corpus** (`outputs/etapa1_corpus/`): base bibliográfica,
   *query* de busca, critérios de inclusão e exclusão, amostragem, documentação
   PRISMA.
2. **Codificação sistemática** (`outputs/etapa2_codificacao/`): codificação em
   três níveis, lexical, tropológico e funcional, sobre o catálogo de nove
   famílias semânticas em `campos_lexicais/catalogo_familias.yaml`.
3. **Análise quantitativa de distribuição** (`outputs/etapa3_distribuicao/`):
   frequência por família, co-ocorrência, redes textuais, distribuição por
   subcampo disciplinar e por período, topic modeling opcional.
4. **Leitura próxima do subcorpus** (`outputs/etapa4_leitura/`): subcorpus de 30
   a 50 artigos lidos nas dimensões argumentativa, genealógica e crítica.

## Famílias semânticas

O catálogo cobre nove famílias: têxtil, biológica/orgânica, mecânica, militar,
oceânica/líquida, religiosa/mística, antropomórfica, mineralógica/extrativa e
caixa/contêiner. A família antropomórfica recebe atenção específica, por ser o
registro dominante e raramente assinalado como figurativo pelos próprios autores.

## Estrutura do repositório

```
campos_lexicais/   catálogo YAML das nove famílias figurativas
codebook/          esquema de codificação tropológica e funcional
corpus/
  queries/         queries versionadas (WoS, Scopus)
  exports/         exportações brutas das bases (não versionado)
  metadata/        metadados consolidados do corpus (CSV)
  txt/             texto integral extraído (não versionado, copyright)
docs/
  decisoes_metodologicas.md   decisões vivas do projeto
  historico.md                índice cronológico
  prisma/                      fluxograma e contagem PRISMA
scripts/           pipeline Python (01 a 07) e _paths.py
outputs/
  etapa1_corpus/ etapa2_codificacao/ etapa3_distribuicao/ etapa4_leitura/
  figuras/  latex/
```

## Como começar

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # ajustar caminhos locais
```

A busca-piloto e a calibração da *query* estão descritas em
`docs/decisoes_metodologicas.md`. Nenhuma etapa avança sem registro de decisão
nesse arquivo.

## Licença e citação

Documento e código sob licença Creative Commons Attribution 4.0 International
(CC BY 4.0). Citações e reusos são bem-vindos com atribuição.

Como citar: HELANSKI, Juliane. *Tramar a inteligência artificial: figurações e
tropos como objeto de análise textual sistemática*. Roteiro de pesquisa.
Campinas: Unicamp, 2026. Versão 1.0.
