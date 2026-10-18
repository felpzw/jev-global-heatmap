"""Leitura local com integridade verificada; nenhuma aquisição durante ranking."""

from dataclasses import dataclass
from hashlib import sha256
import json

from src.services.affinity_schema import CATALOG_VERSION, CriterionEvidence
from src.services.country_registry import COUNTRY_IDS, ROOT, REGISTRY_VERSION


@dataclass(frozen=True)
class Dataset:
    version: str
    fingerprint: str
    manifest: dict
    evidence: dict[tuple[str, str], CriterionEvidence]


def load_dataset() -> Dataset:
    path = ROOT / "data/affinity/v1/manifest.json"
    content = path.read_bytes()
    manifest = json.loads(content)
    if manifest["catalog_version"] != CATALOG_VERSION or manifest["registry_version"] != REGISTRY_VERSION:
        raise ValueError("Versões de catálogo/registro incompatíveis.")
    for relative, digest in manifest["files"].items():
        file = (ROOT / relative).resolve()
        if not file.is_relative_to(ROOT / "data") or sha256(file.read_bytes()).hexdigest() != digest:
            raise ValueError("Falha de integridade do dataset: " + relative)
    records = [CriterionEvidence.model_validate_json(line) for line in
               (ROOT / "data/affinity/v1/evidence.jsonl").read_text(encoding="utf-8").splitlines()]
    if any(e.source_sha256 != manifest["files"].get(e.source_file) for e in records):
        raise ValueError("Proveniência da evidência difere do artefato preservado.")
    index = {(e.iso_alpha_3, e.attribute_id): e for e in records}
    expected = {(iso, attr) for iso in COUNTRY_IDS for attr in ("has_maritime_coast", "english_official")}
    if len(records) != len(index) or set(index) != expected:
        raise ValueError("Dataset exige uma evidência (inclusive missing) para cada país/critério.")
    return Dataset(manifest["dataset_version"], sha256(content).hexdigest(), manifest, index)


def load_demo_dataset() -> Dataset:
    path = ROOT / "data/affinity_demo.json"
    raw = path.read_bytes()
    data = json.loads(raw)
    fingerprint = sha256(raw).hexdigest()
    evidence = {}
    for iso in sorted(COUNTRY_IDS):
        values = data["countries"].get(iso, [None, None])
        for attr, value in zip(("has_maritime_coast", "english_official"), values):
            evidence[(iso, attr)] = CriterionEvidence(
                evidence_id=f"{iso}:{attr}:demo", iso_alpha_3=iso, attribute_id=attr,
                value=value, data_status="missing" if value is None else "observed",
                reason="Fixture fictícia para demonstração; não é evidência factual.",
                source_url="https://example.invalid/synthetic-fixture",
                source_file="data/affinity_demo.json", source_sha256=fingerprint,
                source_revision=data["version"], collected_at="2026-10-18T00:00:00Z",
                license="CC0-1.0 (synthetic fixture)", transformation="synthetic-v1",
            )
    return Dataset(data["version"], fingerprint,
                   {"synthetic": True, "historical": False, "warning": data["warning"]}, evidence)
