# JEV implementation plan and current scope

The foundation, starter dataset, engine and interface were integrated into
`develop` through [PR #22](https://github.com/felpzw/jev-global-heatmap/pull/22).
The next iteration makes the public experience and publication kit English-first.

| Issue | Scope | Status |
| --- | --- | --- |
| #13 | Criteria and local country evidence | Completed for the historical starter snapshot |
| #14 | 195-state registry and strict contracts | Completed |
| #15 | Parsing, filtering, scoring, selection and bounded explanations | Completed |
| #16 | Criteria review, world map, ranking, provenance and export | Completed |
| #17 | Functional evaluation, external relevance, grounding and cost | Offline portion complete; live and human evaluation pending |

## Delivered sequence

1. Preserve the existing data research as a separate commit.
2. Implement the registry, contracts, local snapshot and integrity verification.
3. Implement conservative catalog parsing and deterministic ranking.
4. Limit Gemini to selected explanations, with templates, budget, cache and checkpoints.
5. Integrate reviewable criteria, map, status, source inspection and export.
6. Publish the synthetic protocol, results, CI, portfolio kit and manual handoff.
7. Adapt the UI, natural English requests, country names, explanation output and
   public documentation for an international audience. Preserve source-data hashes
   and supported Portuguese requests.

## Remaining acceptance work

Issue #17 remains open until live model comparison and human evidence/relevance
review are recorded. The [handoff](HANDOFF.md) gives the commands and review steps.
Synthetic results verify behavior; they do not establish API savings or relevance
for arbitrary real-world requests.

The small catalog remains intentional. New concepts need measurable definitions,
licensed evidence and evaluation; see [the extension guide](EXTENDING_JEV.md).
Earlier probability-prediction and LLM-only proposals are preserved in
[the historical documentation](legacy/README.md).
