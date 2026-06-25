# Como fiz a análise de figurações: passo a passo

Documento didático do processo desta análise, escrito para eu mesma explicar, numa
apresentação acadêmica, como cheguei ao contraste figurativo entre a literatura
técnica e a crítica de inteligência artificial. Descreve a pergunta, o corpus, o
catálogo de termos, cada passo do pipeline, o tratamento da homonímia técnica, os
resultados e como reproduzir.

> Nota de escopo (25/06/2026): a primeira rodada de ponta a ponta usou uma amostra
> da OpenAlex de IA em ciências humanas, que é material do projeto irmão
> `bibliometria-ia-humanas`, como ensaio da maquinaria. Aquele corpus, recortado por
> área de conhecimento, capta quem usa IA (engenharia, educação), não quem tematiza
> as figurações da IA, e por isso as figurações não emergiram nele. O corpus próprio
> do Tramar, conforme o roteiro (seção 4.1), é o restritivo metalinguístico: artigos
> de IA que falam de metáfora, figuração, tropo. A maquinaria descrita aqui é a
> mesma; muda o corpus de entrada, constituído pela query restritiva (modo `--busca`
> de `01e_scrape_openalex.py`, ou a `wos_query_v1.txt`).

---

## 1. O que esta análise mede

Eu parto de uma hipótese: a literatura científica sobre IA mobiliza registros
figurativos heterogêneos, e a diferença figurativa entre o polo técnico (Ciência da
Computação, Engenharia) e o polo crítico (Humanidades, Ciências Sociais) funciona
como indício empírico das partições disciplinares do campo. Em vez de afirmar isso
por leitura impressionista, eu meço: conto, em milhares de resumos, com que
frequência cada família de figurações aparece em cada polo.

A figuração têxtil que desenvolvo a partir de Haraway entra como hipótese a testar
sobre o material, não como expectativa a confirmar.

## 2. O corpus: amostra estratificada da OpenAlex

A fonte é a OpenAlex, base bibliográfica aberta, acessada por API sem chave. O
universo de obras de IA em todas as áreas do conhecimento passa de onze milhões, o
que torna o censo completo inviável. Por isso eu amostro, e amostro de forma
estratificada por polo, para que os dois lados do contraste tenham peso comparável:

- polo técnico: campos 17 (Computer Science) e 22 (Engineering);
- polo crítico: campos 12 (Arts and Humanities) e 33 (Social Sciences).

De cada polo eu sorteio 5.000 obras, com `seed=42` para reprodutibilidade, usando a
amostragem aleatória da própria OpenAlex. Para cada obra eu peço o resumo, que a
OpenAlex guarda como índice invertido (`abstract_inverted_index`) e que o pipeline
reconstrói em texto corrido. A janela é 2015 a 2026.

A codificação roda sobre o resumo. Quando o resumo falta, a obra entra com contagem
zero, e eu registro a cobertura de resumo para ser transparente sobre isso.

## 3. As nove famílias figurativas e seus termos

O catálogo (`campos_lexicais/catalogo_familias.yaml`) define nove famílias
semânticas, cada uma com uma lista de termos rastreados por correspondência exata,
com fronteira de palavra e sem sensibilidade a maiúsculas. Os termos centrais de
cada família, em inglês (a versão pt/es do catálogo é rascunho a validar):

- **têxtil**: weave, woven, fabric, thread, knot, fiber, mesh, lace, tapestry,
  quilt, patchwork, seam, stitch, loom, yarn, string figure, e o termo de fronteira
  network.
- **biológica/orgânica**: neural, brain, learning, organism, evolve, mutation,
  ecosystem, growth, neuron, synapse, genetic, cell, organic, adapt.
- **mecânica/industrial**: machine, engine, system, architecture, pipeline,
  infrastructure, framework, scaffold, module, mechanism, gear, apparatus.
- **militar**: deploy, target, weapon, defense, attack, adversarial, strategy,
  operation, surveillance, command, arms race, battlefield, frontier, campaign,
  threat, offensive.
- **oceânica/líquida**: stream, flow, dive, deep, depth, ocean, current, tide,
  fluid, immersion, wave, surface, drift, flood, torrent.
- **religiosa/mística**: oracle, prophet, prophecy, revelation, faith, magic,
  miracle, soul, spirit, conjure, divine, sacred, ritual, alchemy, omniscient,
  sentient.
- **antropomórfica**: intelligent, intelligence, understand, learn, decide,
  hallucinate, dream, reason, think, know, knowledge, attention, memory, perceive,
  believe, aware, imagine, creative, agent.
- **mineralógica/extrativa**: mine, mining, extract, raw, refine, harvest, scrape,
  dig, excavate, ore, quarry, drill, resource, deposit.
- **caixa/contêiner**: black box, container, encapsulate, hidden layer, latent
  space, opaque, transparent, interpretable, explainable, wrapper, sandbox.

A família têxtil é a hipótese do projeto, em diálogo com o catálogo têxtil-feminista
que construo no projeto irmão sobre Latour e Haraway.

## 4. O pipeline, passo a passo

Cada passo é um script numerado em `scripts/`. A sequência:

1. `01e_scrape_openalex.py`: amostra os dois polos da OpenAlex e grava um JSONL de
   obras com resumo. (Variantes: `01_import_wos.py` importa WoS/Scopus/OpenAlex;
   `01d_fetch_openalex.py` busca por uma lista de DOIs; `01c_api_enrich.py` enriquece
   citações e área por DOI.)
2. `02_dedup.py`: remove duplicatas por DOI e, na falta dele, por título normalizado.
3. `03_apply_criteria.py`: aplica os critérios automatizáveis (período, idioma, tipo
   de documento) e marca inclusão e exclusão, com a contagem para o PRISMA.
4. `04_lexical_coding.py`: conta as nove famílias sobre cada resumo, escolhendo a
   lista de termos pela língua do artigo, e gera a matriz artigo por família.
5. `04b_desambiguar.py --gerar`: para as famílias com homonímia técnica
   (antropomórfica e militar), extrai cada ocorrência com seu contexto KWIC, num CSV
   para classificação.
6. `04c_sugerir_desambiguacao.py`: primeiro passe automático que sugere figurativa
   ou técnica por regras de contexto (ver seção 5).
7. `04d_validar_desambiguacao.py`: sorteia uma amostra para eu conferir a acurácia da
   sugestão automática.
8. `04b_desambiguar.py`: aplica a classificação e gera a matriz refinada.
9. `05_cooccurrence.py`: matriz de co-ocorrência entre famílias e rede para Gephi.
10. `06_distribution.py`: distribuição por período e por área disciplinar.
11. `09_contraste_polos.py`: agrupa os campos em polo técnico e crítico e mede as
    ocorrências por família a cada 100 artigos em cada polo.
12. `10_graficos_contraste.py`, `11_redes_polos.py`, `12_radar_polos.py`: as figuras
    de leitura (barras, redes de co-ocorrência por polo, radar de perfil).

Um orquestrador (`run_all.py`) encadeia os passos centrais; o `Makefile` traz os
atalhos.

## 5. O problema da homonímia técnica e a desambiguação

Há um risco que ameaça a contagem bruta: termos como `attention`, `memory`,
`learning`, `intelligence`, `deploy`, `target` são, ao mesmo tempo, vocabulário
técnico literal do campo (uma `attention mechanism`, uma `learning rate`) e
figuração (a máquina que presta atenção, que aprende). A contagem bruta superestima
a figuração, sobretudo no polo técnico.

Eu trato isso no molde da desambiguação `war`/`wars` do projeto sobre Latour: a
contagem fica em duas versões, bruta e refinada, e a camada de classificação fica num
CSV auditável fora do script.

A validação por amostra (`04d`) revelou que um esquema binário (figurativa contra
técnica) era grosso demais. Boa parte das ocorrências que ele chamava de figurativas,
sobretudo no polo crítico, era cognição humana literal: artigos de educação e
psicologia falando de estudantes que aprendem, de pessoas que entendem, do
conhecimento dos pesquisadores. Isso não é a IA personificada, é gente sendo
descrita. Por isso adotei uma classificação em três vias:

- `tecnica`: termo técnico sedimentado, marcado por uma âncora no contexto KWIC
  (`attention` perto de `mechanism`, `target` perto de `variable`);
- `figurativa`: o predicado é atribuído à IA, ao modelo, ao sistema ou ao algoritmo;
- `literal`: o predicado é de um humano ou de uma organização, ou o sujeito é
  indeterminado.

Só a `figurativa` conta na contagem refinada. O passe automático (`04c`) decide pela
âncora técnica e, na falta dela, pelo sujeito mais próximo do termo (IA contra
humano). Cada decisão registra seu motivo, então a regra é auditável.

Dois cuidados metodológicos: a classificação usa só o contexto, nunca o polo do
artigo, para não contaminar o contraste; e as ocorrências classificadas como
figurativas, por terem sujeito de IA, ainda pedem uma conferência entre figuração e
predicado técnico-ML, que eu faço por amostra antes de fixar o resultado.

## 6. O resultado: o contraste figurativo

Sobre a amostra (3.404 artigos técnicos e 2.892 críticos após os critérios), as
ocorrências por 100 artigos, já com a desambiguação aplicada, mostram dois perfis
distintos:

- o polo técnico se estende na **mecânica** (cerca de 100 por 100 artigos), na
  oceânica e na extrativa, registros de máquina, sistema, profundidade e mineração;
- o polo crítico puxa a **antropomórfica** e a **religiosa**.

O achado central está na antropomórfica: ela é quase o dobro no polo crítico (cerca
de 73 contra 38 por 100 artigos), e esse contraste se acentua depois da
desambiguação, em vez de desaparecer. Mesmo descontado todo o vocabulário
técnico-literal, é a literatura das humanas e sociais que mais trata a IA como um
ente que entende, decide, acredita e percebe. Somada à figuração religiosa, também do
lado crítico, desenha-se um polo que personifica e mistifica a IA, em contraste com
um polo técnico de registro mecânico-industrial.

Esse material sustenta empiricamente o bloco de abertura do capítulo 2 da minha tese.

## 7. As visualizações

- **barras divergentes** (`10`): para que polo cada família pende, num só olhar.
- **redes de co-ocorrência por polo** (`11`): como as figurações se agrupam dentro de
  cada polo, com nós dimensionados pela prevalência e arestas pela co-ocorrência.
- **radar de perfil** (`12`): o polígono figurativo de cada polo sobreposto.
- **mapa de calor** (`09`): família por polo, em ocorrências por 100 artigos.

## 8. Como reproduzir

```bash
python -m venv .venv && source .venv/bin/activate   # no Windows: .venv/Scripts/activate
pip install -r requirements.txt

# amostra os dois polos (troque o e-mail)
python scripts/01e_scrape_openalex.py --amostra 5000 --fields "17|22" --email voce@dominio --saida works_tecnico.jsonl
python scripts/01e_scrape_openalex.py --amostra 5000 --fields "12|33" --email voce@dominio --saida works_critico.jsonl

# pipeline
python scripts/01_import_wos.py --fonte works_tecnico.jsonl --base openalex --fonte works_critico.jsonl --base openalex
python scripts/03_apply_criteria.py
python scripts/04_lexical_coding.py
python scripts/04b_desambiguar.py --gerar
python scripts/04c_sugerir_desambiguacao.py --aceitar-tudo
python scripts/04b_desambiguar.py
python scripts/09_contraste_polos.py
python scripts/10_graficos_contraste.py
python scripts/11_redes_polos.py
python scripts/12_radar_polos.py
```

O `seed=42` garante que a amostra e os sorteios se repitam.

## 9. Limites que eu assumo

- A análise corre sobre o resumo, não o texto integral. É um piso da figuração.
- A desambiguação automática é uma heurística, validada por amostra, não um juízo
  fino caso a caso. Onde a amostra revelar erro, eu corrijo à mão.
- A desambiguação de três vias cobre seis famílias: as cognitivas (antropomórfica e
  militar) e as materiais (biológica, têxtil, oceânica, extrativa). As três
  restantes (mecânica, religiosa, caixa) entram na contagem bruta, por terem pouca
  homonímia técnica.
- O catálogo casa formas exatas. Plurais e flexões fora das listas escapam, e a
  cobertura pt/es do catálogo é rascunho a validar.
