# JEV Global Heatmap — LinkedIn and portfolio kit

Prepared on October 18, 2026. Draft material ready for review and publication.

Saved demonstration data: [top five with factors and evidence](evaluations/showcase_summary.json)
and [all 195 registry entries as CSV](evaluations/showcase_ranking.csv). Run
`python -m scripts.export_showcase` to regenerate them; the complete JSON result
is written to `artifacts/showcase_result.json`.

## Project story

How do you turn an intention into a global result that people can inspect?
JEV Global Heatmap converts a supported request into reviewable criteria, applies
requirements and weights to versioned evidence, and displays country affinity
on a world map. The local JEV engine owns scores and ranking. Gemini is an
optional explanation step for selected results.

The project demonstrates separation of responsibilities, strict Pydantic
contracts, reproducible data processing, explicit missing-data handling,
Plotly visualization, Streamlit session state and cancellation, constrained
Gemini integration, failure testing, ranking evaluation and credential-free CI.

## Publishable facts and their limits

| Fact | Evidence | How to describe it |
| --- | --- | --- |
| 195 states: 193 UN members and 2 observers | `data/country_registry.json` | Registry scope, not a guarantee of complete evidence |
| 390 country/criterion positions | `data/affinity/v1/evidence.jsonl` | Includes missing evidence |
| Coastline: 195/195; language: 133/195; 62 gaps | `data/affinity/v1/coverage.json` | Historical extraction coverage, not current factual accuracy |
| Up to 20 candidates and 10 explanations | Contracts and engine tests | Functional limits, not optimized research findings |
| Recall 1.0; precision@3 0.722; NDCG@3 1.0 | `docs/evaluations/affinity_english.json` | Small, synthetic test set only |
| Local p50/p95 latency | Same report, with environment and repetitions | Measurements on the recorded machine, not a production benchmark |
| Gemini tokens and cost | Not measured | No claim of measured API savings |

The current catalog has two boolean attributes. Scores are discrete, with frequent
ties; alphabetical ISO tie-breaking does not imply that one tied country is a
better match. The project demonstrates a bounded, explainable concept search.
The browser needs CDN geometry for the map; `local_only` covers the engine and
explanations. English is the default interface and explanation language, with
continued support for the existing Portuguese input phrases.

## Demo video — 60 to 90 seconds

1. **0–10 s:** “What if an idea could become an explainable world map?” Show the
   interface and enter “I prefer countries with a coastline and English as an
   official language.”
2. **10–25 s:** Review the two criteria and change the coastline weight to 3.
   Explain that scores come from rules and evidence. Confirm the request.
3. **25–40 s:** Calculate. Show the 195 registry entries, selected candidates,
   color scale and countries with insufficient evidence. Hover over the map.
4. **40–55 s:** Open **Criteria and sources**. Inspect a country's values, weights,
   contribution and pinned source. Search for a microstate in the table.
5. **55–70 s:** Switch to “I prefer landlocked countries” and calculate again.
   Show how changing the concept changes the result using the same local engine.
6. **70–90 s:** Show the JSON export and architecture. Explain the current scope:
   two criteria and historical data, with live provider evaluation and human
   review as the next research steps.

Keep the historical-data notice visible in screenshots. Record only project
content and select a frame that shows the map alongside its criteria and context.

## LinkedIn post — ready to edit

What if a search request could become a world map with an explanation behind each result?

I built JEV Global Heatmap to explore that idea.

Start with a request such as “I prefer countries with a coastline and English as
an official language.” Review the criteria, choose what is required, adjust your
preferences, and explore the resulting affinity map.

The local JEV engine applies the requirements and calculates the scores. You can
inspect each country's factors and sources, see where evidence is missing, and
export the result as JSON. When enabled, Gemini receives only the selected
countries to explain their results. The application also works without an API key.

The stack is Python, Pydantic, Streamlit and Plotly, with versioned data,
strict contracts, session caching and automated tests.

The current catalog has two attributes and uses a historical dataset with a
195-state registry. The published evaluation checks functional behavior on
synthetic cases. Real-query relevance and API costs still need a separate study.

For me, the interesting engineering question is how to make concept-based
search inspectable, reproducible and easy to extend.

Which concepts would you add to the map?

Code and setup: https://github.com/felpzw/jev-global-heatmap/tree/develop

#Python #SoftwareEngineering #ArtificialIntelligence #DataVisualization #Portfolio

## Short portfolio description

An explainable concept-search application with a global affinity map,
reviewable criteria and traceable evidence. A deterministic JEV engine ranks a
195-state registry using requirements and weighted preferences. Optional Gemini
explanations are restricted to selected results. Includes reproducible data,
offline tests and a published functional evaluation.

## One-line caption

From a concept to a world map: explore country affinity, inspect the evidence
and understand why each result appears.
