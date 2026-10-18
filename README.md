# JEV Global Heatmap

**Turn an idea into an explainable world map.** JEV translates a supported
request into criteria you can review, applies requirements and weights to local
evidence, and ranks countries by affinity. Gemini can explain the selected
results; the local engine calculates the scores and order.

The starter catalog covers maritime coastline and English as an official
national language. It demonstrates concept-based search with explicit scope,
traceable evidence and visible data gaps.

## Try it locally

Requires Python 3.12+; validated locally with Python 3.14.

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run src/app.py
```

**No API key is required.** Choose an example, review the criteria, confirm them
and click **Calculate global affinity**. The interface, country names, map,
explanations and exported results are in English. Supported Portuguese requests
continue to work.

| Request | What it demonstrates |
| --- | --- |
| I prefer countries with a coastline and English as an official language | Combining concepts and adjusting weights |
| I require a coastline and prefer English as an official language | Filtering by a requirement before ranking preferences |
| I prefer landlocked countries | Negation and a natural English synonym |
| I want beaches and English | Clarification: coastline, beach quality and language proficiency are different concepts |

The map colors every ranked country, highlights selected candidates and
separates exclusions from insufficient data. Search, factors, source details
and JSON cover all 195 states in the registry, including microstates without
representative map geometry. Scores range from 0 to 100 and express affinity
with the confirmed criteria. They are not probabilities.

## Data and explanations

The historical Factbook snapshot has coastline data for 195/195 states and
admissible official-English data for 133/195. The remaining 62 language cases
stay missing. There are 390 country/criterion positions with provenance, hashes
and a reproducible transformation. The Factbook ended in 2026; the archive does
not guarantee current factual validity. Coastline does not measure beach quality;
official language does not measure proficiency. See [sources and policies](data/SOURCES.md).

Choose **Synthetic demonstration** to explore a clearly labeled fixture. With
**Local engine only** enabled, ranking and explanations make no external calls.
The Plotly basemap still requires geometry from a CDN in your browser.

For Gemini explanations, copy `.env.example` to `.env`, configure
`GEMINI_API_KEY` (or `GOOGLE_API_KEY`) and `GEMINI_MODEL`, then disable
**Local engine only**. Verify that the configured model supports Structured
Outputs in your account. Limits are 20 candidates, 10 explanations, one API call,
4,096 output tokens and 30 seconds. Failures fall back to English templates and
preserve scores. Cancellation is cooperative: an in-flight provider request can
still finish. Cache and checkpoints are isolated per session and include the
presentation and prompt versions. Keep credentials out of Git.

## Validation and evaluation

```sh
python -m unittest discover -s tests -v
python -m scripts.verify_dataset
python -m pip check
python evaluate_affinity.py --output artifacts/affinity-evaluation.json
# Optional: up to 36 billable calls; requires your own provider credentials
python evaluate_affinity.py --live --repeats 3 --output artifacts/affinity-live.json
# Regenerate the portfolio summary, ranking CSV and full local result
python -m scripts.export_showcase
```

The [protocol](docs/EVALUATION_PROTOCOL.md) and [English evaluation](docs/evaluations/affinity_english.json)
report candidate recall 1.0, precision@3 0.722 and NDCG@3 1.0 on the synthetic test
set. English cases preserve the original criteria, labels and splits. These
metrics verify controlled functional behavior; they do not establish relevance
for real queries, factual accuracy or API savings. Live Gemini comparison and
human review remain in [the handoff](docs/HANDOFF.md).

## Explore the project

- [Architecture](ARCHITECTURE.md), [contracts and scoring](docs/JEV_DESIGN.md), [delivery plan](docs/JEV_IMPLEMENTATION_PLAN.md) and [extension guide](docs/EXTENDING_JEV.md).
- [LinkedIn and portfolio kit](docs/PORTFOLIO.md): English post, video script, project description, evidence and downloadable data.
- [English experience notes](docs/ENGLISH_EXPERIENCE.md) and [delivery record](docs/DELIVERY.md).
- [Original offline evaluation](docs/evaluations/affinity_offline.json) and [data decision](docs/adr/0004-local-affinity-data.md).
- [Legacy Gemini MVP](docs/MVP_LEGACY.md): `python -m streamlit run src/legacy_app.py`.

Earlier research, issue records and the legacy application are preserved in
[the project history](docs/legacy/README.md), including their original Portuguese text.
