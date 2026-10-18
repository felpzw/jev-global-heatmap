# Extending JEV

The demonstrated flexibility comes from separating concepts, evidence, rules,
selection and explanation. JEV in this repository is a local affinity engine.
Each new concept needs a measurable definition that the user can confirm.

1. Define the attribute, scope, units, admissible evidence and limits. “Good
   beaches” requires its own data and definition; coastline alone is insufficient.
   Record an ADR when changing scoring or evidence semantics.
2. Publish new catalog and dataset versions with licenses, sources, gaps and a
   reproducible transformation. Extend `Attribute` and contract limits when
   adding criteria; the current release supports two booleans.
3. Add English synonyms and ambiguity handling in `input_parser.py`, plus the
   review controls in the UI. Preserve supported Portuguese phrases. Unknown
   terms must remain visible rather than disappearing during parsing.
4. Boolean criteria reuse the comparator and weighted average. Numerical
   indicators require typed evidence and fixed normalization with units,
   direction and limits. Do not derive normalization from the current result set.
5. Add annotated cases split between tuning and testing, including negation,
   missing data, contradictions and requirements. Measure coverage, false
   discards and stable tie-breaking.
6. Keep the explanation adapter restricted to selected results. Extend its
   typed payload and English templates without letting the LLM alter scores or
   ranking. Version changes to presentation and prompts to invalidate stale cache.

Possible research directions include seasonal climate at regional resolution,
economic indicators with explicit periods and comparable digital-infrastructure
evidence. These are future extensions, with no implemented dataset or claims in
this release. Applying the same architecture to cities, products or documents
would require a different registry, contracts and evaluation.
