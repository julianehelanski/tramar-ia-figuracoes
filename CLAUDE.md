# Contexto para Claude Code

Este arquivo é lido automaticamente por Claude Code a cada sessão e mantém
memória do projeto.

---

## Sobre o projeto

Análise textual sistemática das figurações e tropos mobilizados em artigos
científicos sobre inteligência artificial, parte do programa de pesquisa de
Juliane Helanski (Unicamp, Ciências Sociais) sobre o C4AI-USP. O projeto articula
uma escala bibliométrica (constituição de corpus em bases indexadas por critérios
sistemáticos) e uma escala interpretativa-figurativa (leitura próxima do que as
metáforas fazem no texto). Pode operar como artigo autônomo ou como apêndice
metodológico de um documento mais amplo; este repositório assume o desenho de
artigo autônomo.

O projeto é irmão de `analise-figuracoes-latour`: lá o objeto são as obras-fonte
das figurações (Latour, Haraway); aqui o objeto é a literatura de IA que mobiliza
(ou não) essas figurações. O catálogo têxtil-feminista construído no outro
repositório é a nona família semântica deste.

## Sobre a pesquisadora

Juliane é doutoranda em ciências sociais com formação em STS/ANT. Trabalha em
português brasileiro, com leitura em inglês, francês e espanhol. Lê Latour,
Haraway, Stengers, Ingold, Mol, Law, Strathern e Barad como interlocutoras
próximas, e Lakoff e Johnson, Black, Hesse, Crawford, Bender, Suchman como
referencial deste projeto.

## Princípios de trabalho com Juliane (estilo dos textos para a tese e artigo)

1. **Primeira pessoa do singular** em todos os textos produzidos para a tese e o
   artigo (eu, minha pesquisa, meu corpus). Evitar construções impessoais.

2. **Sem travessões `---`** em texto principal. Usar vírgulas, parênteses ou
   dois-pontos. Travessões duplos `--` para intervalos numéricos são aceitáveis.

3. **Sem fórmulas vedadas**: "não X, mas Y", "não apenas X, mas também Y",
   "menos X do que Y", "X, e não Y". Sempre reformular afirmativamente.

4. **Sem adjetivos avaliativos**: marcante, importante, relevante, significativo,
   central, principal, expressivo, complexo (como elogio), problemático.
   Substituir por descritores neutros.

5. **"capítulo" minúsculo** mesmo em referências cruzadas.

6. **Aspas → `\enquote{}`** em LaTeX; nunca aspas inglesas. Aspas internas com
   `\enquote*{}`.

7. **Tom etnográfico**: prosa densa, registro acadêmico, conectores explícitos.
   Sem listas com marcadores em textos para a tese (listas técnicas em README e
   código são aceitas).

8. **Notas de rodapé argumentativas, não suplementares**.

## Como Claude Code deve operar

1. **Não avançar entre etapas sem confirmação explícita da Juliane.**

2. **Documentar decisões em `docs/decisoes_metodologicas.md`** a cada decisão.

3. **Marcar inferências** em relatórios qualitativos com `[INFERÊNCIA]` quando a
   afirmação não tiver citação direta como base. Na leitura próxima (Etapa 4),
   nunca afirmar sem citação direta do artigo.

4. **Seeds aleatórios fixos** em qualquer amostragem ou processo estocástico
   (`seed=42` por padrão). Vale para amostragem de corpus, LDA e BERTopic.

5. **Scripts em Python 3.11+**, com type hints e docstrings em português.

6. **Estilo de código**: PEP 8 com linhas de até 100 caracteres. `black` para
   formatação automática.

7. **Outputs sempre que aplicável em duas versões**: arquivo aberto (CSV,
   Markdown) em `outputs/`, e versão LaTeX em `outputs/latex/`.

8. **Quando houver ambiguidade metodológica, parar e perguntar à Juliane.**

9. **PRISMA e ENTREQ**: documentar a constituição do corpus segundo PRISMA e a
   síntese qualitativa segundo ENTREQ, conforme a seção 6 do roteiro.

## Salvaguardas específicas deste projeto

- **Reflexividade têxtil**: o argumento da figuração têxtil que motiva o projeto
  cria o risco de ver têxtil onde não há. Primeira passagem de codificação é
  cega; cruzamento com categorização externa na segunda; segundo codificador como
  controle de qualidade.

- **Família antropomórfica e homonímia técnica**: termos como *attention*,
  *learning*, *training*, *memory* são vocabulário técnico literal do campo e
  figuração antropomórfica ao mesmo tempo. A contagem lexical bruta superestima a
  figuração. Adotar versão bruta mais camada manual de desambiguação em CSV
  auditável fora do script, no mesmo molde da desambiguação `war`/`wars` do
  projeto Latour.

- **Anais de conferência**: a literatura técnica de IA publica em conferências
  (NeurIPS, ACL, FAccT). Excluir anais subindexaria o polo técnico do contraste.
  Decisão registrada em `docs/decisoes_metodologicas.md`.

- **Assimetria anglófona**: WoS e Scopus indexam predominantemente inglês.
  Tratamento da inclusão de pt/es a explicitar na redação.

## Comandos úteis

```bash
# importar exportação WoS/Scopus e consolidar metadados
python scripts/01_import_wos.py --fonte corpus/exports/wos_2026-06.txt

# deduplicar por DOI e título normalizado
python scripts/02_dedup.py

# aplicar critérios de inclusão/exclusão e gerar contagem PRISMA
python scripts/03_apply_criteria.py

# codificação lexical sobre o catálogo de famílias
python scripts/04_lexical_coding.py
```

## Estrutura do repositório

Ver `README.md`. Convenções herdadas de `analise-figuracoes-latour`: catálogo
único em `campos_lexicais/`, decisões vivas em `docs/decisoes_metodologicas.md`,
índice cronológico em `docs/historico.md`, scripts numerados reutilizáveis.
