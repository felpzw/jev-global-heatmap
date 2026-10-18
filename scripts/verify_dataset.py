"""Verify byte-identical reconstruction, hashes and coverage without changing the checkout."""

import json

from scripts.build_dataset import build
from src.services.country_registry import ROOT, load_registry
from src.services.evidence_service import load_dataset


def verify():
    manifest = ROOT / "data/affinity/v1/manifest.json"
    paths = [ROOT / p for p in json.loads(manifest.read_text())["files"]] + [manifest]
    before = {p: p.read_bytes() for p in paths}
    try:
        build()
        changed = [str(p.relative_to(ROOT)) for p in paths if p.read_bytes() != before[p]]
        if changed:
            raise ValueError("Reconstruction differs: " + ", ".join(changed))
        load_registry()
        data = load_dataset()
        print(f"Identical reconstruction: {len(data.evidence)} evidence records; {data.fingerprint}")
    finally:
        # Verification never publishes a different snapshot version.
        for p, content in before.items():
            if p.read_bytes() != content:
                p.write_bytes(content)


if __name__ == "__main__":
    verify()
