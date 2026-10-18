# Delivery and issue evaluation record

The original JEV implementation was integrated into `develop` through
[PR #22](https://github.com/felpzw/jev-global-heatmap/pull/22) on October 18, 2026.
The initial uncommitted research was preserved in commit `62bf4db`; no stashes
were present or discarded. Commits were grouped by data/foundation, engine,
interface and evaluation/documentation.

| Issue | Technical outcome | Evidence and limit |
| --- | --- | --- |
| #13 — Data | Completed for the starter catalog | 390 positions; coastline 195/195 and official English 133/195; extracts, hashes and offline reconstruction; historical sources without a complete human factual audit |
| #14 — Foundation | Completed | Exact 195-state scope, strict contracts, independent score/status/selection/explanation, finite values and JSON round-trip |
| #15 — Engine | Completed | Conservative parser, confirmed criteria, requirements, weighted score, stable ISO ties, bounded explanations, templates, session cache, checkpoints and cooperative cancellation |
| #16 — Interface | Completed | Map, ranking, evidence, source inspection, 195-state search, synthetic fixture and JSON; browser basemap uses CDN |
| #17 — Evaluation | Offline portion complete; external acceptance pending | Fixed synthetic cases, baseline and ranking/latency metrics; live Gemini comparison and human review remain in the handoff |

## English adaptation

The interface, map, country names, explanations, errors, runtime evidence notes,
showcase exports and public documentation now use English. Natural English
queries support requirements, preferences, coastline/landlocked synonyms and
negation, with existing Portuguese input compatibility. Presentation and prompt
versions prevent reuse of older explanations. Published source hashes are unchanged.

The [English experience notes](ENGLISH_EXPERIENCE.md) describe the scope and tests.
The [English evaluation](evaluations/affinity_english.json) keeps the original
labels and splits: candidate recall 1.0, precision@3 0.722 and NDCG@3 1.0 on the
synthetic test set. The precision aggregate includes the empty-result case.
There were no annotated false discards or requirement violations. Parity with
the simple baseline does not establish superiority or real-query relevance.

## Verification

- The original delivery passed 61 offline tests and GitHub Actions.
- The English iteration passes 69 tests, including natural English parsing,
  country search, export language, SDK instructions, presentation-cache
  invalidation, preserved source values and Portuguese query compatibility.
- `scripts.verify_dataset` confirms byte-identical source-data reconstruction.
- `pip check` verifies installed dependency consistency; Markdown links and
  `git diff --check` are checked before integration.
- GitHub Actions runs integrity checks, tests and evaluation without API keys.
  Remote integration and check status are recorded in the delivery PR.

Manual acceptance work is in [HANDOFF.md](HANDOFF.md). Publication material,
video script and demonstration exports are in [PORTFOLIO.md](PORTFOLIO.md).
Issue #17 stays open until the live measurements and human review are available.
