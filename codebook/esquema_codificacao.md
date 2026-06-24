# Esquema de codificação

Codificação em três níveis articulados, conforme a Etapa 2 do roteiro. O nível
lexical é automatizável pelo catálogo de famílias; os níveis tropológico e
funcional são de codificação manual sobre o subcorpus, com segundo codificador
como controle de qualidade.

## Princípio de validade

Primeira passagem **cega**: codificar sem expectativa prévia da figuração têxtil.
Segunda passagem: cruzar com categorização externa (ontologia de metáforas em
ciência da computação, quando disponível). Terceira: segundo codificador sobre
amostra. Concordância intercodificadores registrada (Cohen ou Krippendorff) em
`outputs/etapa2_codificacao/concordancia.md`.

## Nível 1: lexical (automatizado)

Sobre cada artigo, contar ocorrências por família semântica do catálogo
(`campos_lexicais/catalogo_familias.yaml`). Saída: matriz artigo × família, bruta
e, para as famílias `antropomorfica` e `militar`, desambiguada (ver decisão 3 em
`docs/decisoes_metodologicas.md`).

## Nível 2: tropológico (manual, subcorpus)

Para cada artigo do subcorpus, registrar em planilha:

| Campo | Descrição |
| :---- | :---- |
| `id_artigo` | identificador do corpus |
| `figuracao_dominante` | metáfora que estrutura o argumento central |
| `marcador` | explícito (like, as, metaphor, analogy) ou implícito/naturalizado |
| `familia` | família semântica do catálogo |
| `genealogia` | autor/tradição que a figuração ativa, se citado |
| `tensao_figurativa` | há figurações concorrentes? gestos de denaturalização? |
| `citacao` | trecho literal que sustenta a codificação (obrigatório) |

## Nível 3: funcional (manual, subcorpus)

Para cada figuração identificada no nível 2, registrar a função no argumento
(marcação múltipla permitida):

| Código | Função |
| :---- | :---- |
| `FAM` | tornar familiar o desconhecido (analogia explicativa) |
| `NAT` | naturalizar o objeto (apresentar como dado o que é construído) |
| `ANT` | antropomorfizar (atribuir capacidades humanas ao sistema) |
| `POL` | politizar (mostrar poder, extração, exclusão) |
| `POS` | posicionar disciplinarmente (filiar a tradição teórica) |

## Saídas

- `outputs/etapa2_codificacao/codificacao_lexical.csv` (nível 1)
- `outputs/etapa2_codificacao/codificacao_tropologica.csv` (nível 2)
- `outputs/etapa2_codificacao/codificacao_funcional.csv` (nível 3)
- `outputs/etapa2_codificacao/desambiguacao_antropomorfica.csv`
- `outputs/etapa2_codificacao/desambiguacao_militar.csv`
