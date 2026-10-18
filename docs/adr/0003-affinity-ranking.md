# ADR 0003 — JEV affinity ranking with optional LLM explanations

- Decision date: October 5, 2026; starter catalog implemented October 18, 2026.
- Status: accepted and implemented; external evaluation remains in #17.
- Supersedes ADR 0002 and the probability-prediction scope.
- Architecture issue: [#20](https://github.com/felpzw/jev-global-heatmap/issues/20).

## Decision

The product ranks affinity with a confirmed request. JEV interprets supported
criteria, filters requirements, calculates 0–100 scores from weighted preferences
and selects candidates. Gemini receives only the explanation subset and its
evidence. It cannot select countries, calculate scores or change order.

The score is affinity under explicit data and rules, not the probability of an
event. The starter catalog uses conservative phrases and a versioned local
snapshot. Unknown or ambiguous concepts require clarification.

## Consequences

- Requirements and preferences have separate roles.
- Missing data and exclusions have null scores; valid low affinity can be zero.
- Every final response contains the 195-state registry, with bounded explanations.
- Templates keep the ranking useful without credentials or after provider failure.
- Embeddings, LLM interpretation and LLM reranking are deferred until evidence
  establishes their need.
- Evaluation covers selection, ranking, grounding and cost/latency; probability
  calibration, forecast horizons, Brier score and log loss are outside scope.
- Candidate limits are functional hypotheses, not evidence of savings.

Earlier architecture decisions remain in the project history. The English
presentation changes names and explanatory text while preserving scoring and
source-data semantics. See [architecture](../../ARCHITECTURE.md),
[contracts](../JEV_DESIGN.md), [plan](../JEV_IMPLEMENTATION_PLAN.md) and
[the legacy MVP](../MVP_LEGACY.md).
