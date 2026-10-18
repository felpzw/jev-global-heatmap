# English experience

The public application and publication kit use English by default. This is an
English-first release of the existing deterministic JEV flow, with continued
support for its Portuguese input phrases.

## What changed

- Interface, examples, review controls, status messages, map labels, table columns,
  country search, templates, source notes and exported presentation use English.
- The parser accepts natural phrases including “English as an official language”,
  “I require a coastline”, “landlocked countries”, “not landlocked” and
  “countries that don't have a coastline”. Ambiguity, unsupported terms,
  conflicting criteria and alternative conditions still require clarification.
- Gemini is asked to explain in English. Both the restricted JEV adapter and
  the optional broad evaluation baseline use the same output language.
- English country names come from the existing registry's `name_en` field.
- The README, architecture, scoring guide, evaluation protocol, source guide,
  extension guide and LinkedIn/portfolio kit are available in English.

## Version and data integrity

Published source files, catalog, evidence snapshot, original query labels and
source hashes remain unchanged. Runtime evidence notes are English descriptions
of the same extraction rules. New results and showcase exports identify
`presentation_version: en-v1`. The prompt version is `evidence-only-en-v2`.
Cache identities include presentation and prompt versions, so old Portuguese
explanations are not reused for an English run.

English evaluation cases are in `data/affinity_evaluation_cases_en.json`.
They preserve original IDs, criteria, grades and tune/test splits. The original
Portuguese case file and offline report remain available. Historical research,
issue records and the legacy MVP retain their original text.

## Verification

Regression tests cover English queries and negation, English names and evidence,
unchanged source values/hashes, English SDK instructions, cached-presentation
invalidation, country search and Portuguese input compatibility. Run:

```sh
python -m unittest discover -s tests -v
python -m scripts.verify_dataset
python evaluate_affinity.py --output artifacts/affinity-english.json
```

The same restrictions apply: a two-attribute catalog, historical country-level
evidence, a CDN-dependent basemap and pending live/human evaluation in #17.
