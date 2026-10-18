# Data sources, provenance and reproduction

Demonstration release: `factbook-archive-v1`. The registry contains 193 UN member
states plus the Holy See/VAT and Palestine/PSE. Dependencies, Kosovo and Taiwan
are outside the scoring registry. Plotly geometry can represent additional
units without changing the registry.

## Sources and licenses

| Artifact | Source and reuse | Transformation |
| --- | --- | --- |
| `sources/factbook_extract.json` | Public-domain US government facts, mirrored by [factbook.json](https://github.com/factbook/factbook.json), revision `144d6977b2b01ac1cbd220de754c0a005616760b`; [mirror's CC0 license](https://github.com/factbook/factbook.json/blob/144d6977b2b01ac1cbd220de754c0a005616760b/LICENSE.md) | Selected Coastline, Languages and country-identity fields; hashes of original profiles and local artifacts |
| `sources/factbook_routes.json` | Explicit mapping from internal ISO IDs to public profile paths | ISO alpha-2 checked against each profile's Internet country code; GBR accepts `.uk`; PSE combines Gaza and the West Bank |
| `country_registry.json` | Names, codes and translations from [pycountry](https://github.com/pycountry/pycountry), based on Debian iso-codes, LGPL 2.1 or later | Explicit 195-state scope; three-character M49 strings; [license](licenses/pycountry-LGPL-2.1.txt) and [copyright](licenses/pycountry-COPYRIGHT.txt) retained |
| `affinity_demo.json` | Original synthetic fixture, CC0-1.0 | Eight states with fictional values; other entries remain missing |
| `criteria_catalog.json` | Original definitions and rules | Two boolean attributes, equality comparison, 0/1 normalization and explicit missing values |

Registry scope follows the [UN member list](https://www.un.org/en/about-us/member-states)
and [observer-state references](https://research.un.org/en/unmembers/observers).
Their text and tables are not redistributed. The project does not bundle the
third-party full country-code table whose reuse terms were uncertain.

The CIA announced the [Factbook's end on February 4, 2026](https://www.cia.gov/stories/story/spotlighting-the-world-factbook-as-we-bid-a-fond-farewell/).
Collection time and mirror revision are distinct from a fact's publication date
and validity. `published_at` is null because these fields provide no single
publication date. Dates within raw source text are preserved. The release uses
conservative automatic derivation without a complete human factual audit.

## Extraction rules

- Coastline: `0 km`/`landlocked` means false; a positive distance means true.
  KAZ/AZE/TKM explicitly describe their Caspian/Aral boundaries as landlocked.
  PSE uses the boolean `any` of Gaza and West Bank values. Dependencies are not
  aggregated into their parent state.
- Language: an explicit `English (official)` marker, including `English only`, or
  explicit national/subsidiary-official wording means true. An official-language
  list without an English mention means false. Inconclusive status, an English
  mention without official status or disagreement between profiles stays missing.
  Translated sample text is not evidence of an official language. De facto
  English remains missing when the required status is not established.
- `missing`, `conflicting`, `expired` and `not_applicable` do not score. The first
  release contains only observed/missing values; contracts reserve the other states.
- Joint coverage for both criteria is 133/195; coastline alone is 195/195.
  Coastline has 151 true/44 false values; official English has 47 true/86 false.
  Coverage measures admissible extraction, not accuracy or current validity.
- The historical snapshot remains usable as a labeled demonstration. Current
  factual use requires review and a new data release.

## Rebuild and update

```sh
# Offline: verify byte-for-byte reconstruction and integrity of the existing release
python -m scripts.verify_dataset
# Derive local artifacts while preparing a new release
python -m scripts.build_dataset
# Optional explicit acquisition: 196 profiles, 4 workers, 30 s and 2 MB per file
python -m scripts.acquire_factbook
```

Ranking never acquires data. Preserved extracts allow offline reconstruction of
evidence, coverage and the manifest. Pinned URLs and original hashes support
profile-level audits. The manifest identifies the transformation-code hash.

Review corrections and replacement sources monthly; the closed archive will not
receive official updates. Changes to values, criteria or sources require a new
release, hashes and a diff report. Keep published releases immutable. Local Git
snapshots are sufficient for this volume; a server database and scheduler are
unnecessary. Session checkpoints live outside Git in `artifacts/`.

## English presentation

The published catalog, registry and evidence files retain their original bytes.
The application uses the registry's existing `name_en` names and translates
explanatory notes after integrity verification. Values, source identifiers,
period semantics, ISO codes and hashes do not change. New results identify
`presentation_version: en-v1`; earlier Portuguese artifacts remain reproducible.
