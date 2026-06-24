# Decisões metodológicas

Documento vivo. Cada decisão tomada no projeto é registrada aqui, com data e
justificativa. Decisões pendentes ficam marcadas como tal, com as opções em jogo,
para que eu (Juliane) as resolva antes da etapa correspondente.

---

## 1. Escopo e desenho (24/06/2026)

Adotado o desenho de **artigo autônomo** (versão completa, 7.000 a 9.000 palavras
na saída final), com as quatro etapas plenas. A saída de apêndice metodológico
permanece possível como derivação condensada posterior.

A figuração têxtil que desenvolvo em outros trabalhos entra como **hipótese a ser
testada empiricamente** sobre o corpus, não como expectativa a confirmar. Adoto a
segunda opção do ponto de atenção sobre articulação com a tese (seção 6 do
roteiro): o projeto roda depois da tese, e o argumento dela opera como hipótese.

## 2. Decisões pendentes (a resolver antes da Etapa 1)

Registro aqui os pontos que pedem decisão minha, levantados na leitura do roteiro.
Nenhuma busca definitiva roda antes de fechá-los.

### 2.a. Anais de conferência: incluir ou excluir

Tensão: o critério de exclusão do roteiro descarta anais, mas a literatura técnica
de IA publica majoritariamente em conferências revisadas por pares (NeurIPS, ACL,
FAccT, AAAI). O artigo de Bender e colegas (2021) sobre *stochastic parrots*,
citado na bibliografia base, é um *paper* de conferência (FAccT). Excluir anais
subindexa o polo técnico do contraste técnico/crítico.

Opções: (i) flexibilizar o critério para incluir anais indexados com revisão por
pares (a própria seção 4.1 admite a exceção); (ii) manter a exclusão e assumir que
WoS recorta o campo pelo polo formal-periódico, usando arXiv/ACM como base
paralela para o polo técnico.

Estado: **resolvido em 24/06/2026** pela opção (i). Decido incluir anais indexados
com revisão por pares, mantendo `"Proceedings Paper"` em `DT` na *query* e o tipo
correspondente entre os incluídos em `03_apply_criteria.py`. Sustento a escolha em
três razões: preservo um fluxo PRISMA único, evito a heterogeneidade de qualidade
que o preprint introduziria, e capturo o polo técnico dentro da própria base
sistemática, já que a WoS indexa as conferências de referência (FAccT, NeurIPS,
ACL, AAAI) pelo Conference Proceedings Citation Index. Deixo o arXiv como
complemento condicionado: se a busca-piloto mostrar lacuna de cobertura no polo
técnico, retomo a opção (ii) como camada paralela, registrada como nova decisão.
Detalhe operacional em `docs/decisoes_metodologicas.md` (seção 6, abaixo).

### 2.b. Estratégia de query: restritiva, ampla ou híbrida

A restritiva analisa o que a literatura diz sobre figurações (corpus pequeno,
metalinguístico). A ampla analisa o uso implícito (corpus grande, exige
amostragem). A híbrida contrasta as duas, ao custo de dobrar a constituição de
corpus e manter dois fluxos PRISMA. A coerência com o objetivo geral (contrastar
o vocabulário técnico com o crítico) aponta para a híbrida.

Estado: **resolvido em 24/06/2026** pela híbrida faseada. Começo pela restritiva,
que já está pronta em `corpus/queries/wos_query_v1.txt`, e rodo a busca-piloto para
dimensionar o retorno. A ampla entra em seguida, com amostragem proporcional ao
volume, e mantenho dois fluxos PRISMA quando ela entrar. Condiciono a ampla ao que
a piloto mostrar: se o corpus restritivo já sustentar o contraste técnico contra
crítico com densidade suficiente, registro a ampla como camada posterior; se o
metalinguístico vier escasso, antecipo a ampla. A decisão de antecipar ou adiar
fica para depois da piloto, como nova entrada datada.

### 2.c. Bases e idioma

Decidir se WoS basta na Etapa 1 ou se Scopus e arXiv entram desde já, e se a busca
inclui português e espanhol ou se pt/es ficam como camada de comparação posterior.
A assimetria anglófona deve ser explicitada na redação de todo modo (seção 6 do
roteiro).

Estado: **resolvido em 24/06/2026**. Sobre as bases, adoto WoS e Scopus na Etapa 1.
Duas bases indexadas reduzem o viés de fonte única, e o pipeline já importa e
deduplica as duas por DOI. O arXiv fica condicionado ao gatilho da decisão 2.a:
entra como base paralela se a busca-piloto revelar lacuna de cobertura no polo
técnico. Sobre o idioma, incluo inglês, português e espanhol desde a Etapa 1, com a
`query` mantendo `LA=(English OR Portuguese OR Spanish)`. Essa escolha tem uma
consequência que operacionalizo na seção 7: o catálogo de famílias, antes só em
inglês, ganhou listas de termos em pt e es, e a codificação passou a escolher a
lista pela língua do artigo. As listas pt/es são rascunho a validar antes de
codificar qualquer corpus dessas línguas. A assimetria anglófona da literatura fica
explicitada na redação de todo modo.

### 2.d. Amostragem do subcorpus para a leitura próxima

A seleção do quintil superior por citações enviesa para artigos antigos (mais
tempo de acúmulo) e contra os de 2024 a 2026. Há também a distância entre o que a
citação mede, influência acumulada, e o que a leitura próxima procura, densidade
figurativa.

Estado: **resolvido em 24/06/2026** pela amostragem teórica por densidade
figurativa. Decido selecionar o subcorpus de 30 a 50 artigos por amostragem
orientada por informação, no sentido que Flyvbjerg dá ao termo: privilegio os
casos que carregam mais figuração, medida pela contagem da Etapa 2, em vez de
representatividade estatística ou impacto. A seleção fica estratificada por
período e por estrato disciplinar, para que a leitura cubra a variação do campo e
não só os artigos mais densos de um único nicho. Mantenho a contagem de citações
como descritor secundário no subcorpus, registrada para contextualização, sem
peso na seleção. Operacionalização em `scripts/08_sample_subcorpus.py` e detalhe
em `docs/decisoes_metodologicas.md` (seção 6, abaixo).

## 3. Família antropomórfica e homonímia técnica (24/06/2026)

Decisão fixada: a família antropomórfica (e a militar, por `deploy`/`target`/
`operation`) terá contagem em duas versões, bruta e desambiguada. A camada manual
de classificação fica em CSV auditável fora do script
(`outputs/etapa2_codificacao/desambiguacao_<familia>.csv`, coluna
`categoria_final`), lida e aplicada pelo pipeline, nunca recomputada. Molde herdado
da desambiguação `war`/`wars` do projeto `analise-figuracoes-latour`. Justificativa:
termos como *attention*, *memory*, *learning* e *intelligence* são vocabulário
técnico literal do campo e figuração antropomórfica ao mesmo tempo; a contagem
lexical bruta superestima a figuração.

## 4. Catálogo de famílias (24/06/2026)

Catálogo inicial com nove famílias em `campos_lexicais/catalogo_familias.yaml`,
transposto da tabela da seção 4.2 do roteiro, com termos de fronteira anotados
(`network`, `deep`, `pipeline`, `black box`, `latent space`). Catálogo aberto:
expansões registradas em `docs/historico.md`.

## 5. Reprodutibilidade (24/06/2026)

Seed fixo `seed=42` em qualquer amostragem ou processo estocástico (amostragem de
corpus, LDA, BERTopic). Documentação da constituição de corpus segundo PRISMA
(`docs/prisma/`), síntese qualitativa segundo ENTREQ.

## 6. Operacionalização das decisões 2.a e 2.d (24/06/2026)

Registro aqui como as duas decisões resolvidas hoje se traduzem no pipeline, para
manter a rastreabilidade entre a escolha metodológica e o código.

Sobre 2.a, anais de conferência: o tipo `Proceedings Paper` permanece em
`TIPOS_INCLUIDOS` no passo `03_apply_criteria.py` e em `DT` na *query* v1. Os
critérios automatizáveis aceitam o anais; a triagem manual posterior, sobre
presença de análise textual e reflexão epistêmica, decide artigo a artigo, do
mesmo modo que decide para periódicos. A condição que reabriria a opção (ii) fica
explícita: lacuna de cobertura do polo técnico revelada pela busca-piloto, caso em
que eu acrescento o arXiv como base paralela e abro um segundo fluxo PRISMA.

Sobre 2.d, amostragem do subcorpus: o passo `08_sample_subcorpus.py` lê a matriz
de codificação (refinada quando existe, bruta caso contrário) e os metadados,
calcula uma medida de densidade figurativa por artigo (soma das ocorrências das
nove famílias dividida pelo comprimento do resumo em palavras, para não premiar só
resumos longos), estratifica por período e por estrato disciplinar, e seleciona em
cada estrato os artigos de maior densidade até compor o alvo de 30 a 50. A contagem
de citações entra como coluna descritiva no resultado, sem peso na ordenação. O
seed fixo `seed=42` governa o desempate. A definição operacional do polo técnico
contra o crítico fica como dependência aberta: por ora o estrato disciplinar usa a
categoria WoS; quando eu fixar o indicador de polo, ele entra como coluna de
estratificação adicional, registrada como nova decisão.

## 7. Catálogo multilíngue (24/06/2026)

A decisão 2.c de incluir português e espanhol na Etapa 1 obriga o catálogo a deixar
de ser monolíngue. Estendi `campos_lexicais/catalogo_familias.yaml` com listas
`termos_pt` e `termos_es` por família, e exclusões por língua (`exclusoes_pt`,
`exclusoes_es`). A codificação (`04_lexical_coding.py`) e a desambiguação
(`04b_desambiguar.py`) escolhem a lista pela coluna `idioma` do artigo, com recuo
para o inglês quando a lista da língua falta.

Trato as listas pt e es como **rascunho v0 a validar**. Eu mesma reviso as
traduções das famílias antes de codificar qualquer corpus pt ou es, porque a
correspondência figurativa entre línguas pede julgamento que a tradução automática
não resolve: o têxtil de Haraway em português, o vocabulário extrativo de Crawford
em espanhol, a fronteira de `rede`/`red` contra `network`. Enquanto eu não validar,
a contagem desses corpora permanece provisória.

Duas refinações ficam registradas para a calibração. A primeira: a correspondência
hoje distingue acento, então `máquina` com acento e `maquina` sem acento contam como
formas diferentes; decido na calibração se normalizo acentos antes da contagem ou se
exijo entrada acentuada. A segunda: a correspondência casa formas exatas, então
flexões e plurais (`tejemos` ao lado de `tejer`, `aprende` ao lado de `aprender`)
escapam; a mesma decisão entre ampliar as listas ou lematizar, já anotada para o
inglês, vale para pt e es.
