"""Avaliação offline de fixtures ou comparação real entre dois prompts."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from statistics import mean, pstdev
from time import perf_counter

import pycountry

from src.services.llm_client import HeatmapError, configured_model, generate_heatmap, parse_response
from src.services.prompts import BASELINE_PROMPT, SYSTEM_PROMPT
from src.services.schema import HeatmapResponse

CASES_PATH = Path(__file__).resolve().parent / "data/evaluation_cases.json"


def score_metrics(response: HeatmapResponse) -> dict:
    scores = [country.heat_score for country in response.countries]
    return {
        "countries": len(scores),
        "score_min": min(scores) if scores else None,
        "score_max": max(scores) if scores else None,
        "score_mean": round(mean(scores), 2) if scores else None,
        "score_stddev": round(pstdev(scores), 2) if scores else None,
        "score_distribution": {
            "0–<25": sum(0 <= score < 25 for score in scores),
            "25–<50": sum(25 <= score < 50 for score in scores),
            "50–<75": sum(50 <= score < 75 for score in scores),
            "75–100": sum(75 <= score <= 100 for score in scores),
        },
    }


def evaluate_offline(cases: list[dict]) -> list[dict]:
    results = []
    for case in cases:
        text = json.dumps(case["response"], ensure_ascii=False)
        codes = [country["iso_alpha_3"] for country in case["response"]["countries"]]
        record = {
            "case": case["id"], "prompt_variant": "fixture",
            "iso_codes_total": len(codes),
            "iso_codes_valid": sum(pycountry.countries.get(alpha_3=code) is not None for code in codes),
        }
        start = perf_counter()
        try:
            response = parse_response(text)
        except HeatmapError as error:
            elapsed = perf_counter() - start
            record.update(validation_ok=False, error=str(error))
        else:
            elapsed = perf_counter() - start
            record.update(validation_ok=True, **score_metrics(response))
        record["local_validation_ms"] = round(elapsed * 1000, 3)
        record["fixture_check_passed"] = record["validation_ok"] == case["expected_valid"]
        results.append(record)
    return results


def evaluate_live(cases: list[dict], repeats: int) -> list[dict]:
    results = []
    variants = [("baseline", BASELINE_PROMPT), ("refined", SYSTEM_PROMPT)]
    for repetition in range(repeats):
        # Alternate order to reduce systematic effects of warm-up/provider load.
        order = variants if repetition % 2 == 0 else list(reversed(variants))
        for case in cases:
            if case.get("offline_only"):
                continue
            for name, prompt in order:
                record = {"case": case["id"], "context": case["context"],
                          "prompt_variant": name, "repetition": repetition + 1}
                start = perf_counter()
                try:
                    response = generate_heatmap(case["context"], system_prompt=prompt)
                except HeatmapError as error:
                    record.update(validation_ok=False, error=str(error))
                else:
                    record.update(
                        validation_ok=True, **score_metrics(response),
                        iso_codes_total=len(response.countries),
                        iso_codes_valid=len(response.countries), response=response.model_dump(),
                    )
                record["end_to_end_seconds"] = round(perf_counter() - start, 3)
                results.append(record)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Faz chamadas reais à API; pode gerar custos.")
    parser.add_argument("--repeats", type=int, choices=range(1, 6), default=1)
    parser.add_argument("--output", type=Path, default=Path("artifacts/prompt_evaluation.json"))
    args = parser.parse_args()
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    results = evaluate_live(cases, args.repeats) if args.live else evaluate_offline(cases)
    report = {
        "mode": "live" if args.live else "offline_fixtures",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model": configured_model() if args.live else None,
        "quality_assessment": "pending_manual_review" if args.live else "not_measured",
        "note": (
            "Inspecione as justificativas e confirme fatos antes de concluir sobre qualidade."
            if args.live else
            "Dados fictícios: mede apenas validação local, não qualidade do modelo ou latência da API."
        ),
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Relatório {report['mode']}: {args.output}")
    return 0 if all(row["validation_ok"] if args.live else row["fixture_check_passed"] for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
