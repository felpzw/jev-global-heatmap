# JEV design — criteria, affinity and explanations

The implemented catalog supports maritime coastline and English as an official
national language. English is the default UI and output language; supported
Portuguese query phrases remain accepted. Ambiguous or unknown concepts require
review before execution. A request needs at least one scored preference.

“Beaches and English” does not establish beach quality or proficiency. The user
must explicitly choose the supported coastline and official-language attributes
if those represent the intended request.

## Contracts

| Model | Fields and responsibility |
| --- | --- |
| `AffinityRequest` | Original text, criteria (`attribute_id`, `expected`, `role`, `weight`), confirmation, local mode, threshold and limits |
| `CriterionEvidence` | Evidence ID, country, attribute, nullable boolean, data status, reason and source provenance |
| `AffinityFactor` | Criterion, evidence, normalized match and weighted contribution |
| `CountryAffinity` | Country, English name, nullable score/rank, status, factors, selection and explanation |
| `CandidateExplanation` | Country ID, English text and relevant evidence IDs |
| `RunMetadata` | Dataset/hash, registry/catalog/ranker/schema/presentation versions, cache identity, optional provider/model/prompt, metrics and errors |
| `AffinityResponse` | Run ID/status, confirmed request, metadata, all 195 countries, ordered candidate IDs and explanation IDs |

Contracts are separate from the legacy `HeatmapResponse`. Strict types, finite
numbers, positive weights, duplicates, exact registry membership and valid
country/evidence relationships are checked. M49 remains a three-character string.
Country names are display labels; ISO IDs remain the integration keys.

## Filtering and scoring

1. Validate the confirmed request, weights, limits and dataset integrity.
2. Exclude a state only if observed evidence fails a requirement.
3. Otherwise, incomplete evidence for an active criterion yields insufficient data.
4. Score complete eligible states with
   `100 * sum(weight_i * normalized_i) / sum(weight_i)` over preferences only.
5. Order by unrounded descending score, then ascending ISO alpha-3 code.

For a boolean criterion, normalization is 1 when the observed value matches the
desired value and 0 otherwise. Non-observed data stays null. The engine neither
imputes zero nor reweights around absent attributes. Exported factors contain
all weights, normalized values and contributions needed to reproduce the score.
Rounding is presentation only.

| Country status | Score | Meaning |
| --- | --- | --- |
| `ranked` | Finite 0–100 | Eligible and scored, including valid zero scores |
| `filtered_out` | null | An observed value fails a requirement |
| `insufficient_data` | null | Evidence is missing for an active criterion |
| `error` | null | A technical country-level failure, reserved by the contract |

## Selection and explanations

Candidates meet the threshold and retain ranking order. Limits are
`1 <= candidate_limit <= 20`, `0 <= explanation_limit <= 10`, and
`explanation_limit <= candidate_limit`. Explanation IDs are the ordered prefix
of candidate IDs. An empty explanation set makes no provider call.

The Gemini payload contains confirmed typed criteria, selected country IDs,
local scores and relevant typed evidence. It excludes the free-form request and
raw source text. Output must match the exact requested country order and valid
evidence IDs; the schema has no score fields. Schema validity does not prove
factual grounding, which still requires human review.

Explanation states are `generated`, `template`, `not_requested` and `error`.
Provider failures preserve scores and ranking, mark the run partial, and retain
an English template with source `template`. Without a key or in local mode,
requested explanations use templates without a provider call.

## Execution and language versions

The budget is one call, 4,096 output tokens and 30 seconds, with no additional
retries. Cancellation is checked while ranking and before/after the provider
call; it cannot abort a request already sent. The previous UI result is preserved.
Atomic checkpoints allow resuming with the same identities and record consumed
provider budget when cancellation happens after a call.

Cache keys include request, dataset hash, scoring/catalog versions, limits,
model, prompt and English presentation version. Source-data artifacts stay
immutable. English country names and evidence notes are applied at runtime;
new exports identify `presentation_version: en-v1`. The explanation prompt is
`evidence-only-en-v2`. Repeated UI reruns reuse the stored result and figure.

## Map and evaluation

The map colors every ranked state on a fixed 0–100 scale and outlines selected
candidates. Exclusions, missing data, errors and outside-registry geometry have
distinct presentations. Search and the evidence table cover microstates even
where map geometry is absent.

The [evaluation protocol](EVALUATION_PROTOCOL.md) defines candidate recall,
precision@3, NDCG@3, requirements, false discards and latency on fixed synthetic
cases. English case translations preserve the original labels and splits.
Live cost and grounding review remain in [HANDOFF.md](HANDOFF.md).
