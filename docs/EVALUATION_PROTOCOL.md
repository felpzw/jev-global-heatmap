# Affinity evaluation protocol — English v2

English adaptation of the protocol defined on October 18, 2026. The English
queries are fixed before running the localized evaluation. Criteria, weights,
labels, splits and acceptance targets match the original protocol.

The offline experiment checks functional behavior with synthetic fixtures and
explicit expected labels. It does not measure user-perceived relevance, source
truth, universal semantic search or monetary savings.

- Dataset: `synthetic-demo-v1`; eight states have defined fixture values and the
  other registry positions remain missing. Registry size: 195; catalog:
  `coast-language-v1`.
- Cases: `data/affinity_evaluation_cases_en.json`, version
  `synthetic-affinity-cases-en-v2`. One tuning case, six test cases and two
  clarification requests. The Portuguese cases remain available for comparison.
- Report K: 3. Selection: threshold 50, at most 20 candidates and 10 explanations.
  The empty case uses threshold 1 and its explicitly declared criteria.
- Relevance: grade 3 for a complete match, 1 for an explicitly relevant partial
  match, and 0 for a non-relevant fixture entry. An absent label is not a negative
  factual statement about a real country.
- Metrics: candidate recall, precision@3 with a fixed denominator of 3, NDCG@3
  with gain `2**grade - 1`, false discards and requirement violations. Recall and
  NDCG are null for an empty relevant set; selection should be empty.
- Functional targets: zero requirement violations, zero annotated false discards,
  zero local-mode API calls, clarification for every ambiguity case and ranking
  parity with the independent simple baseline on the annotated cases. Parity
  does not demonstrate superiority.
- Baseline: an unweighted match-count rule using the same boolean evidence,
  requirements and complete-data policy. Report differences when present.
- Latency: five repetitions per query, without cache and with session cache;
  linearly interpolated percentiles. Acquisition, network and UI time are
  excluded from the local ranking measurement. Record environment and versions.

`--live --repeats 3` adds an alternating comparison of JEV with restricted
explanations versus broad Gemini, using the same model, confirmed criteria and
synthetic evidence. Broad Gemini sees all 195 positions, including gaps, and
calculates selection and explanations. JEV calculates scores locally and sends
only the selected explanation subset. Both variants request English output,
with 4,096 output tokens, a 30-second timeout and one attempt per call.

The variants ask the model to do different work; this evaluates an architectural
choice rather than isolating prompt length alone. Record truncation as failure,
not as savings. Record actual tokens when available, latency and output for
review. Cost stays null without a verified tariff. Live execution can incur
provider charges.

A human reviewer should classify every claim as supported, unsupported or
inconclusive; check evidence IDs, ranking and requirements; and record reviewer
and date. Synthetic labels do not replace judgments on independent real queries.
Review the historical snapshot's current validity before making external quality
claims. Live cost and human review remain pending without credentials and a reviewer.

The [original report](evaluations/affinity_offline.json) belongs to the earlier
Portuguese run. The [English report](evaluations/affinity_english.json) records
its own protocol, evaluator and case hashes; source-data hashes stay unchanged.
