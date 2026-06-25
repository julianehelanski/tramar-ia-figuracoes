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

## Sinais que sobrevivem aos três corpora

Mesmo onde a figuração não organiza o campo, dois traços reaparecem:
- a **mecânica** marca o polo técnico em todos os corpora (a IA técnica é
  mecânico-industrial: system, architecture, e, na robótica, hand, arm, joint);
- a **caixa** e a **religiosa** pendem, fracas mas consistentes, ao polo crítico (a
  opacidade, a caixa-preta, o oráculo).

## O próximo recorte: o polo crítico por comunidade

A operacionalização correta de literatura crítica é por filiação, não por palavra:
recortar o polo crítico pelos periódicos que abrigam esse discurso (Big Data &
Society, Science Technology & Human Values, Social Studies of Science, AI & Society,
New Media & Society) e contrastá-lo com um polo técnico de veículos de computação. É o
passo seguinte, com a busca por fonte da OpenAlex.

## Quadro dos corpora

| Corpus | Recorte | Artigos | Polos pela keyness |
| :--- | :--- | :--- | :--- |
| 1 | amostra por área (17,22 vs 12,33) | 6.296 | engenharia × educação |
| 2 | busca metalinguística no título | 1.258 | robótica × linguística da metáfora |
| 3 | por periódico crítico (a constituir) | --- | computação × crítica STS |

As figuras de cada corpus (contraste por família e keyness) ficam em
`outputs/figuras/`, geradas pelos passos `09`, `10` e `13`.
