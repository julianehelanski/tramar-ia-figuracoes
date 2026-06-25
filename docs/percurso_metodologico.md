# Percurso metodológico: três corpora e onde a figuração vive

Registro reflexivo do percurso de constituição do corpus do Tramar, escrito como
material da própria pesquisa. Documento como tentei localizar empiricamente a tensão
figural entre a literatura técnica e a crítica de IA, o que cada tentativa revelou, e
a que conclusão de método cheguei. O percurso é parte do argumento, não acessório
dele: ele mostra onde a figuração se deixa contar e onde ela escapa à contagem.

---

## A pergunta operacional

Quero medir se a diferença figurativa entre a literatura técnica e a crítica de IA
funciona como indício das partições do campo. Para medir, preciso de um corpus que
contenha os dois polos. A pergunta prática, que se mostrou o nó de todo o percurso, é:
como recortar, numa base indexada, a literatura crítica de IA, a do registro
material-semiótico de Haraway, Latour, Crawford, Suchman?

## Corpus 1: amostra estratificada por área de conhecimento

Constituí uma amostra global da OpenAlex do conceito de IA, estratificada por polo
disciplinar: campos 17 e 22 (Computação, Engenharia) como técnico, campos 12 e 33
(Artes e Humanidades, Ciências Sociais) como crítico, 5.000 obras por polo, com
`seed=42`. Após dedup e critérios, 6.296 artigos.

A análise textual indutiva (keyness por log-verossimilhança, sem usar o catálogo)
mostrou que os polos se distinguem assim: o técnico por algorithm, detection, system,
network, signal, neural; o crítico por students, teachers, school, education,
teaching, children. O polo crítico operacionalizado por área é, na verdade, pesquisa
em educação que usa IA, não a crítica material-semiótica. Nenhum termo do catálogo
figurativo apareceu entre as palavras distintivas. A figuração não emergiu porque o
corpus não era o lugar dela.

Achado: a estratificação por área capta quem usa IA, não quem tematiza suas
figurações. A antropomorfização que parecia alta no polo crítico era cognição humana
literal das ciências da educação (estudantes que aprendem, pesquisadores que sabem).

## Corpus 2: busca metalinguística no título

Constituí então o corpus restritivo do roteiro: obras de IA cujo título tematiza
figuração, por busca em `title.search` com metaphor, figuration, trope,
anthropomorphic, personification, figurative. A população foi 18.659; baixei e
processei 1.258 artigos incluídos.

A keyness deste corpus mostrou dois polos que de fato falam de figuração, mas não os
que eu procurava: o técnico por hand, robotic, grasping, finger, prosthetic, ou seja,
robótica antropomórfica (robôs com forma humana); o crítico por metaphor, conceptual,
corpus, discourse, semantic, linguistic, ou seja, estudos linguísticos da metáfora
(metáfora conceitual à Lakoff, linguística de corpus). A crítica material-semiótica
de STS continua marginal.

Achado: o próprio vocabulário metalinguístico é homônimo. metaphor é tarefa de
processamento de linguagem natural, anthropomorphic é morfologia de robô, figurative
é NLP de linguagem figurada. A busca por palavra não separa o registro crítico-STS,
porque a palavra é compartilhada com a engenharia e a linguística computacional.

## A conclusão de método

Três recortes (amostra por área, busca em título e resumo, busca em título) batem na
mesma parede: a figuração crítica-STS não é isolável por palavra-chave nem por área de
conhecimento. Ela é um nicho identificado por periódico, autor e citação, não por
vocabulário. No nível da literatura indexada, o discurso explícito sobre figuração em
IA é robótica e linguística da metáfora, e a crítica material-semiótica fica à margem.

Isso reorganiza o argumento, e a favor: a tensão figural entre o têxtil-feminista e o
militar-industrial não é um fenômeno bibliométrico de massa, distribuído pelo campo.
Ela vive em textos teóricos específicos e num nicho crítico pequeno. A escala
bibliométrica serve para mostrar o que a figuração faz quando se torna operacional
(robótica, NLP) e o que ela é quando permanece marginal (a crítica). A leitura próxima
das obras-fonte, que é o que faço no projeto irmão `analise-figuracoes-latour`, é onde
a tensão se deixa ler.

## Corpus 3: recorte por periódico (o terreno certo)

Operacionalizei o polo crítico por filiação, não por palavra: o polo crítico pelos
periódicos que abrigam o discurso crítico-STS (Big Data & Society, Science Technology
& Human Values, Social Studies of Science, AI & Society, New Media & Society, por
ISSN), e o polo técnico por uma amostra de IA em Computação e Engenharia (campos 17 e
22, `seed=42`). O polo passou a ser atribuído na importação, por fonte, não pela área
do artigo. Após dedup e critérios, 7.057 artigos críticos e 3.404 técnicos.

É o primeiro corpus em que a figuração crítica aparece com nitidez. As ocorrências por
100 artigos, já desambiguadas:

| família | crítico | técnico |
| :--- | ---: | ---: |
| caixa | 8,28 | 2,94 |
| mecânica | 36,98 | 99,94 |
| têxtil | 6,89 | 16,83 |
| antropomórfica | 10,46 | 12,40 |
| oceânica | 10,40 | 25,94 |
| biológica | 10,12 | 27,67 |
| extrativa | 2,73 | 6,23 |
| militar | 2,68 | 5,73 |
| religiosa | 1,18 | 0,62 |

A **caixa** pende ao crítico (8,28 contra 2,94): a literatura crítica figura a IA como
caixa-preta, no eixo opacidade contra transparência, a crítica da accountability
algorítmica. A **mecânica** marca o técnico. A **antropomórfica** ficou par entre os
polos, o que desfaz a leitura inicial de que a crítica antropomorfiza mais. A **têxtil**
no crítico (6,89) é, quando lida, a figuração haraweana e latouriana de fato:
\enquote{grounded in actor-network theory}, \enquote{the fabric of biological and
social existence}, \enquote{the current patchwork of European regulatory frameworks}.
O número técnico da têxtil (16,83) ainda carrega resíduo de \enquote{network} de
engenharia, a apertar.

Achado: a figuração crítica não some, ela estava no corpus errado. Recortada por
comunidade, emerge como caixa-preta (opacidade) e como rede material-semiótica
(actor-network, fabric, patchwork). A tensão figural se deixa contar quando o recorte
é por filiação, não por vocabulário nem por área.

## Sinais que sobrevivem aos três corpora

Mesmo onde a figuração não organiza o campo, dois traços reaparecem:
- a **mecânica** marca o polo técnico em todos os corpora (a IA técnica é
  mecânico-industrial: system, architecture, e, na robótica, hand, arm, joint);
- a **caixa** e a **religiosa** pendem, fracas mas consistentes, ao polo crítico (a
  opacidade, a caixa-preta, o oráculo). No corpus 3, a caixa se firma.

## Quadro dos corpora

| Corpus | Recorte | Artigos | Polos |
| :--- | :--- | :--- | :--- |
| 1 | amostra por área (17,22 vs 12,33) | 6.296 | engenharia × educação |
| 2 | busca metalinguística no título | 1.258 | robótica × linguística da metáfora |
| 3 | por periódico (ISSN crítico vs campos 17,22) | 10.461 | crítica STS × computação |

## A rede de Louvain do corpus 3 (a separação emerge sozinha)

Rodei o `14` (rede de co-ocorrência por força de associação) sobre o corpus 3. A rede
ficou com 60 termos e 104 arestas, particionada em seis comunidades, com modularidade
0,509, acima do limiar de 0,3 que tomo como estrutura de comunidades legítima. As seis
comunidades, pelas dez palavras de maior frequência de cada:

| comunidade | termos de cabeça | leitura |
| :--- | :--- | :--- |
| 2 | learning, performance, network, algorithm, machine, accuracy, networks | núcleo técnico-computacional (aprendizado de máquina, desempenho) |
| 0 | how, technology, public, political, understanding, role, critical | discurso crítico-STS (tecnologia como questão pública) |
| 3 | social, media, digital, online, users, content, platforms, platform | estudos de plataforma e mídia digital |
| 1 | systems, human, ai, control, artificial, intelligence | eixo IA/humano/controle (vizinhança compartilhada entre os polos) |
| 5 | data, research, information, practices, development, future | práticas de dados e de pesquisa |
| 4 | time, real, world | periférico (resíduo de \enquote{real-time}, \enquote{real world}) |

A separação técnico contra crítico que não se deixava isolar por palavra-chave nem por
área de conhecimento emerge sozinha quando deixo a rede se organizar por co-ocorrência:
a comunidade 2 é o léxico do desempenho computacional, as comunidades 0 e 3 são o léxico
crítico-cultural, e elas se destacam por modularidade. É a contraprova indutiva do
recorte por periódico, pois o corpus 3 contém os dois registros e a rede os separa. A
comunidade 1 (IA, humano, controle) é a vizinhança comum, por onde circula a
antropomórfica, o que combina com ela ter ficado par no contraste por família. Figura em
`outputs/figuras/rede_louvain.png`, comunidades em
`outputs/exploratorio/comunidades_louvain.csv`.

## Ponto de retomada (sessão de 25/06/2026)

O corpus 3 (por periódico) está montado, com o contraste do `09`, a keyness do `13` e a
rede de Louvain do `14` rodados (modularidade 0,509, seis comunidades legíveis). Pende,
para a próxima sessão: a AFC famílias × polo sobre este corpus, e a leitura final para a
apresentação.

Os corpora são regeneráveis (a máquina perdeu os arquivos locais, não o método):

```bash
# polo crítico por periódico (censo)
python scripts/01e_scrape_openalex.py --sem-conceito \
  --issn "2053-9517|0951-5666|1435-5655|0162-2439|1552-8251|0306-3127|1460-3659|1461-4448|1461-7315" \
  --email voce@dominio --saida works_critico_venues.jsonl

# polo técnico (amostra, seed fixo -> idêntica)
python scripts/01e_scrape_openalex.py --amostra 5000 --fields "17|22" \
  --email voce@dominio --saida works_tecnico.jsonl

# importar com polo por fonte e rodar o pipeline
python scripts/01_import_wos.py --fonte works_critico_venues.jsonl --base openalex --polo crítico
python scripts/01_import_wos.py --fonte works_tecnico.jsonl --base openalex --polo técnico --append
python scripts/02_dedup.py && python scripts/03_apply_criteria.py && python scripts/04_lexical_coding.py
python scripts/04b_desambiguar.py --gerar && python scripts/04c_sugerir_desambiguacao.py --aceitar-tudo
python scripts/04b_desambiguar.py && python scripts/09_contraste_polos.py
python scripts/13_analise_textual_exploratoria.py --top 30
python scripts/14_rede_louvain.py
```

As figuras de cada corpus (contraste por família e keyness) ficam em
`outputs/figuras/`, geradas pelos passos `09`, `10` e `13`.
