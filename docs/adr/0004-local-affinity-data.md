# ADR 0004 — Local affinity-data snapshots

- Proposed October 5, 2026; accepted October 18, 2026 for the demonstration release.
- Data issue: [#13](https://github.com/felpzw/jev-global-heatmap/issues/13).
- Depends on [ADR 0003](0003-affinity-ranking.md) and #14 contracts.
- Original investigation: [DATA_RESEARCH.md](../DATA_RESEARCH.md), preserved in Portuguese.

## Decision

Use JSON for the catalog, registry, extracts and manifest, and JSONL for evidence.
Keep small permitted artifacts in Git as complete, immutable published snapshots.
Ranking verifies hashes and loads an index by country and attribute. Acquisition
is an explicit command outside ranking. This volume does not require a server
database or online queries.

Release `factbook-archive-v1` uses public Factbook fields from revision
`144d6977b2b01ac1cbd220de754c0a005616760b`, with preserved extracts, pinned URLs,
original profile hashes and a transformation-code hash. The investigated full
country-code table is not redistributed. Profile routing is checked against
the profiles' Internet country code field. PSE combines Gaza and the West Bank.

The Factbook ended in 2026; the release is historical, without a guarantee of
current validity. Inconclusive, de facto or missing official-language status
stays missing. Beach quality and proficiency are outside the implemented catalog.
Sources, licenses and territorial policy are in [SOURCES.md](../../data/SOURCES.md).

## Pilot evidence and alternatives

There are 390 country/criterion positions: 195/195 coastline values and 133/195
admissible official-English values, with 62 explicit language gaps. Offline
byte-for-byte reconstruction passes `scripts.verify_dataset`. Extraction
coverage does not establish factual accuracy or current validity.

CSV is an export format. SQLite could be a derived store if history or queries
justify it. Parquet/DuckDB remain candidates for larger analytical workloads.
JSON/JSONL supports review but requires explicit validation of relationships
and release-wide integrity.

Changes to sources, values, catalog or transformation require a new release and
hashes. Retain the extracts needed for reproduction. Rollback uses a previous
version and invalidates caches by identity. English presentation is applied at
runtime and does not rewrite published source files.
