# Ranking e RRF

Criado em: 2026-10-18 · Atualizado em: 2026-10-18

## O que é ranking

Ranking é a ordem dos resultados de uma busca. O primeiro resultado é aquele que o mecanismo priorizou segundo seus critérios. Isso não significa que ele necessariamente responda à pergunta.

Na [busca híbrida](busca-hibrida.md), a busca vetorial e a textual podem produzir ordens diferentes. Como distância vetorial e pontuação textual têm significados e escalas distintos, somar seus valores diretamente exige cuidados. Uma alternativa é combinar as posições dos resultados.

## O que é RRF

RRF significa *Reciprocal Rank Fusion*, ou fusão por posições recíprocas. Na forma simples, cada resultado recebe uma contribuição de cada lista em que aparece:

```text
score(d) = soma de 1 / (K + posição de d em cada lista)
```

As posições começam em 1. `K` é uma constante que reduz a diferença entre as contribuições das primeiras posições; não é a quantidade de resultados recuperados. Se um trecho não aparece em uma lista, essa lista não contribui para seu score.

O RRF usa posições, sem precisar comparar diretamente as escalas dos scores originais. Veja a [documentação do RRFReranker do LanceDB](https://docs.lancedb.com/reranking/rrf).

## Exemplo concreto

Considere duas listas hipotéticas e `K = 60`:

| Trecho | Posição vetorial | Posição textual | Score RRF aproximado |
|---|---|---|---|
| A | 1 | Ausente | `1/61 = 0,01639` |
| B | 2 | 1 | `1/62 + 1/61 = 0,03252` |
| C | Ausente | 2 | `1/62 = 0,01613` |

O trecho B fica primeiro porque aparece bem colocado nas duas listas. O trecho A pode continuar sendo relevante, mesmo com score próximo de 0,016. Esses números ilustram a fórmula; não são medições do projeto.

## Como aparece no TCC

Em [database_utility.py](../../backend/database_utility.py), a consulta híbrida não chama `.rerank()` explicitamente. A [documentação atual de busca híbrida do LanceDB](https://docs.lancedb.com/search/hybrid-search) informa RRF como padrão. Portanto, o código delega essa escolha à biblioteca; não fixa a constante nem implementa a fórmula por conta própria.

O campo `_relevance_score` é lido para exibição com `--debug_rag`. Ele não é usado para descartar trechos. Os resultados retornados são reunidos no contexto enviado ao modelo.

## Ranking não é confiança

Um score de `0,016` não significa 1,6% de probabilidade de a resposta estar correta. O RRF resume posições nas listas recuperadas; não mede correção clínica, qualidade do documento ou suficiência do contexto.

Um corte arbitrário pode eliminar uma evidência útil encontrada por apenas uma das buscas. A adequação de qualquer filtro precisa ser avaliada com perguntas e evidências de referência.

Também é possível que todas as opções recuperadas sejam inadequadas: ainda assim, haverá uma primeira colocada. Decidir quando responder ou recusar é outro problema, explicado em [grounding e abstenção](grounding-e-abstencao.md).

## Conceitos relacionados

- [Busca híbrida](busca-hibrida.md).
- [Avaliação de RAG](avaliacao-de-rag.md).
