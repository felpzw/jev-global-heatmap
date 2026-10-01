"""Smoke test real: python test_llm.py [tema]. Não é executado pelos testes offline."""

import argparse
import sys
from time import perf_counter

from src.services.llm_client import HeatmapError, generate_heatmap


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("context", nargs="?", default="Adoção de carros elétricos")
    args = parser.parse_args()
    start = perf_counter()
    try:
        result = generate_heatmap(args.context)
    except HeatmapError as error:
        print(str(error), file=sys.stderr)
        return 1
    print(result.model_dump_json(indent=2))
    print(f"Países válidos: {len(result.countries)} | Tempo: {perf_counter() - start:.2f}s", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
