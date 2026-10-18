"""Exporta evidências pequenas da demonstração sem chamadas externas."""

from collections import Counter
import csv
import json

from src.services.affinity_schema import AffinityRequest, Criterion
from src.services.country_registry import ROOT
from src.services.jev_service import run_affinity


def main():
    response = run_affinity(AffinityRequest(
        text="I prefer countries with a coastline and English as an official language", confirmed=True,
        criteria=[Criterion(attribute_id="has_maritime_coast", weight=3.0),
                  Criterion(attribute_id="english_official")]))
    rows = sorted(response.countries, key=lambda c: (c.rank is None, c.rank or 0, c.iso_alpha_3))
    folder = ROOT / "docs/evaluations"
    summary = {"request": response.request.model_dump(),
               "dataset_version": response.metadata.dataset_version,
               "presentation_version": response.metadata.presentation_version,
               "dataset_sha256": response.metadata.dataset_sha256,
               "status_counts": dict(Counter(c.status for c in rows)),
               "score_distribution": dict(Counter(str(c.affinity_score) for c in rows if c.status == "ranked")),
               "candidate_ids": response.candidate_ids, "explanation_ids": response.explanation_ids,
               "llm_calls": response.metadata.metrics.calls,
               "top_five": [c.model_dump() for c in rows[:5]],
               "warning": "Historical snapshot; alphabetical ISO tie-breaking does not imply merit. Current factual validity has not been verified."}
    (folder / "showcase_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (folder / "showcase_ranking.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["iso_alpha_3", "name", "rank", "affinity_score", "status", "selection", "explanation_source"])
        writer.writerows([c.iso_alpha_3, c.name, c.rank, c.affinity_score, c.status, c.selection,
                         c.explanation_source] for c in rows)
    artifact = ROOT / "artifacts/showcase_result.json"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(response.model_dump_json(indent=2), encoding="utf-8")
    print(f"Exported 195 records; summary and CSV: {folder}; full JSON: {artifact}.")


if __name__ == "__main__":
    main()
