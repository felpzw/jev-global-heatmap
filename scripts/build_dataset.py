"""Reconstrói registro, evidências, manifesto e cobertura sem rede."""

from collections import Counter
from hashlib import sha256
import gettext
import html
import json
import re

import pycountry

from src.services.country_registry import COUNTRY_IDS, REGISTRY_VERSION, ROOT
from src.services.affinity_schema import CriterionEvidence, CATALOG_VERSION

ATTRIBUTES = ("has_maritime_coast", "english_official")


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def plain(value):
    return html.unescape(re.sub(r"<[^>]+>", " ", value)).strip()


def coastline(profiles):
    values = []
    for p in profiles:
        text = plain(p["coastline"].get("text", ""))
        if re.match(r"^0(?:\s|\b)", text) or "landlocked" in text.lower():
            values.append(False)
        elif re.match(r"^[\d,.]+\s*km", text):
            values.append(True)
        else:
            return None
    return any(values) if values else None


def english(profiles):
    values = []
    for p in profiles:
        language = p["languages"]
        text = plain(language.get("text", language.get("Languages", {}).get("text", "")))
        note = plain(language.get("note", ""))
        explicit = re.search(r"\bEnglish(?: only)?\s*\(official(?:\s|[,;)])", text, re.I)
        explicit_note = re.search(r"\bEnglish (?:is the (?:subsidiary )?official(?: national)? language|are official languages)", text + " " + note, re.I)
        if explicit or explicit_note:
            values.append(True)
        elif "english" not in text.lower() and "(official" in text.lower():
            values.append(False)
        else:
            # Inglês sem status nacional explícito ou inglês regional não vira true/false.
            return None
    return values[0] if values and len(set(values)) == 1 else None


def build():
    source_path = ROOT / "data/sources/factbook_extract.json"
    source_bytes = source_path.read_bytes()
    source = json.loads(source_bytes)
    source_hash = sha256(source_bytes).hexdigest()
    mapping = ROOT / source["mapping_file"]
    if sha256(mapping.read_bytes()).hexdigest() != source["mapping_sha256"]:
        raise ValueError("Hash da correspondência GEC/ISO inválido.")
    records = source["countries"]
    if len(records) != 195 or {r["iso_alpha_3"] for r in records} != COUNTRY_IDS:
        raise ValueError("Extração deve corresponder ao registro completo.")
    translation = gettext.translation("iso3166-1", pycountry.LOCALES_DIR, languages=["pt"], fallback=True)
    countries = []
    for iso in sorted(COUNTRY_IDS):
        c = pycountry.countries.get(alpha_3=iso)
        countries.append({"iso_alpha_3": iso, "m49": c.numeric,
                          "name": translation.gettext(c.name), "name_en": c.name,
                          "un_status": "observer" if iso in {"PSE", "VAT"} else "member"})
    write_json(ROOT / "data/country_registry.json", {
        "version": REGISTRY_VERSION, "reviewed_at": "2026-10-18",
        "sources": ["https://www.un.org/en/about-us/member-states",
                    "https://research.un.org/en/unmembers/observers",
                    "https://unstats.un.org/unsd/methodology/m49/overview/"],
        "code_source": f"pycountry {pycountry.__version__}", "countries": countries,
    })
    evidence = []
    for record in records:
        iso = record["iso_alpha_3"]
        profiles = record["profiles"]
        for attr, transform in zip(ATTRIBUTES, (coastline, english)):
            value = transform(profiles)
            reason = ("Derivado de Coastline: zero/landlocked = false; km positivo = true. Lagos e Cáspio não são litoral marítimo."
                      if attr == "has_maritime_coast" else
                      "Lista Languages: English (official) = true; lista oficial sem inglês = false; demais casos = missing.")
            if value is None:
                reason = "Fonte não comprova o atributo no escopo nacional; sem imputação. " + reason
            evidence.append(CriterionEvidence(
                evidence_id=f"{iso}:{attr}:v1", iso_alpha_3=iso, attribute_id=attr,
                value=value, data_status="observed" if value is not None else "missing",
                reason=reason, source_url=profiles[0]["url"] if profiles else None,
                source_file="data/sources/factbook_extract.json", source_sha256=source_hash,
                source_revision=source["revision"], collected_at=source["collected_at"],
                published_at=None, reference_period="Arquivo Factbook; datas específicas não fornecidas para estes campos",
                license=source["license"],
            ).model_dump())
    folder = ROOT / "data/affinity/v1"
    folder.mkdir(parents=True, exist_ok=True)
    content = "".join(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n" for e in evidence)
    (folder / "evidence.jsonl").write_text(content, encoding="utf-8")
    coverage = {attr: dict(Counter(e["data_status"] for e in evidence if e["attribute_id"] == attr))
                for attr in ATTRIBUTES}
    gaps = {attr: [e["iso_alpha_3"] for e in evidence if e["attribute_id"] == attr and e["value"] is None]
            for attr in ATTRIBUTES}
    write_json(folder / "coverage.json", {"denominator": 195, "coverage": coverage, "gaps": gaps,
        "values": {attr: {str(v).lower(): sum(e["value"] is v for e in evidence if e["attribute_id"] == attr)
                          for v in (True, False)} for attr in ATTRIBUTES}})
    files = ["data/affinity/v1/evidence.jsonl", "data/affinity/v1/coverage.json",
             "data/country_registry.json", "data/criteria_catalog.json",
             "data/sources/factbook_extract.json", "data/sources/factbook_routes.json"]
    write_json(folder / "manifest.json", {
        "dataset_version": "factbook-archive-v1", "catalog_version": CATALOG_VERSION,
        "registry_version": REGISTRY_VERSION, "transform_version": "factbook-extract-v1",
        "transform_sha256": sha256((ROOT / "scripts/build_dataset.py").read_bytes()).hexdigest(),
        "collected_at": source["collected_at"], "source_revision": source["revision"],
        "historical": True, "synthetic": False,
        "warning": "Snapshot histórico do Factbook encerrado em 2026. Verificar vigência antes de usos reais. Litoral não mede praia; idioma oficial não mede proficiência.",
        "files": {f: sha256((ROOT / f).read_bytes()).hexdigest() for f in files},
    })
    print(json.dumps(coverage, ensure_ascii=False))


if __name__ == "__main__":
    build()
