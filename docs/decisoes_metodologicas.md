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

Estado: **pendente**. A *query* v1 inclui `"Proceedings Paper"` em `DT` como gancho
da opção (i); remover esse termo realiza a opção (ii).

### 2.b. Estratégia de query: restritiva, ampla ou híbrida

A restritiva analisa o que a literatura diz sobre figurações (corpus pequeno,
metalinguístico). A ampla analisa o uso implícito (corpus grande, exige
amostragem). A híbrida contrasta as duas, ao custo de dobrar a constituição de
corpus e manter dois fluxos PRISMA. A coerência com o objetivo geral (contrastar
o vocabulário técnico com o crítico) aponta para a híbrida.

Estado: **pendente**. A *query* v1 (`corpus/queries/wos_query_v1.txt`) é a
restritiva refinada. Decidir se a ampla entra já na Etapa 1 ou fica para a versão
artigo. Sugestão de trabalho: começar pela restritiva, rodar busca-piloto, decidir
a ampla à luz do volume retornado.

### 2.c. Bases e idioma

Decidir se WoS basta na Etapa 1 ou se Scopus e arXiv entram desde já, e se a busca
inclui português e espanhol ou se pt/es ficam como camada de comparação posterior.
A assimetria anglófona deve ser explicitada na redação de todo modo (seção 6 do
roteiro).

Estado: **pendente**. A *query* v1 inclui `LA=(English OR Portuguese OR Spanish)`
como ponto de partida; restringir a inglês é um ajuste de uma linha.

### 2.d. Amostragem por citação

A seleção do quintil superior por citações enviesa para artigos antigos (mais
tempo de acúmulo) e contra os de 2024 a 2026. Se adotada, combinar com a
amostragem temporal prevista para corrigir o viés de recência.

Estado: **pendente**, decidir na transição Etapa 1 para Etapa 4.

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
