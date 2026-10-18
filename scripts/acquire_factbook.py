"""Aquisição opcional e limitada. A reconstrução normal não acessa a rede.

Execute na raiz: python -m scripts.acquire_factbook
Preserva somente os dois campos públicos necessários, com hash do perfil original.
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import json
import re
from urllib.request import Request, urlopen

import pycountry

from src.services.country_registry import COUNTRY_IDS, ROOT

FACTBOOK_REVISION = "144d6977b2b01ac1cbd220de754c0a005616760b"
RAW = "https://raw.githubusercontent.com/"


def fetch(url: str) -> bytes:
    with urlopen(Request(url, headers={"User-Agent": "JEV-portfolio-dataset/1.0"}), timeout=30) as response:
        data = response.read(2_000_001)
    if len(data) > 2_000_000:
        raise ValueError("Artefato excedeu limite de 2 MB.")
    return data


def acquire():
    routes_file = ROOT / "data/sources/factbook_routes.json"
    mapping = json.loads(routes_file.read_text(encoding="utf-8"))
    if set(mapping) != COUNTRY_IDS or sum(map(len, mapping.values())) != 196:
        raise ValueError("Roteamento exige 195 Estados e 196 perfis (Gaza + Cisjordânia).")
    collected = datetime.now(timezone.utc).isoformat()

    def profile(item):
        iso, paths = item
        records = []
        for path in paths:
            if not re.fullmatch(r"[a-z-]+/[a-z]{2}\.json", path):
                raise ValueError("Caminho de perfil inválido.")
            url = f"{RAW}factbook/factbook.json/{FACTBOOK_REVISION}/{path}"
            raw = fetch(url)
            data = json.loads(raw)
            internet = data.get("Communications", {}).get("Internet country code", {})
            expected = "." + pycountry.countries.get(alpha_3=iso).alpha_2.lower()
            acceptable = {expected, ".uk"} if iso == "GBR" else {expected}
            domains = set(re.findall(r"\.[a-z]{2}(?![a-z])", internet.get("text", "").lower()))
            if not domains & acceptable:
                raise ValueError(f"Perfil {iso}/{path}: código de internet incompatível: {internet}")
            records.append({"path": path, "url": url, "sha256": sha256(raw).hexdigest(),
                            "country_name": data.get("Government", {}).get("Country name", {}),
                            "internet_country_code": internet,
                            "coastline": data.get("Geography", {}).get("Coastline", {}),
                            "languages": data.get("People and Society", {}).get("Languages", {})})
        return {"iso_alpha_3": iso, "profiles": records}

    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(profile, mapping.items()))
    result = {"revision": FACTBOOK_REVISION, "collected_at": collected,
              "published_at": None, "license": "Public domain (US government facts)",
              "publication_note": "Datas de vigência variam por campo; não inferidas da coleta. Arquivo histórico, sem garantia de vigência atual.",
              "mapping_file": "data/sources/factbook_routes.json",
              "mapping_sha256": sha256(routes_file.read_bytes()).hexdigest(),
              "mapping_validation": "ISO alpha-2 conferido contra Communications/Internet country code de cada perfil público; GBR permite .uk; PSE agrega gz+we.",
              "countries": records}
    target = ROOT / "data/sources/factbook_extract.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(records)} Estados; {sum(len(r['profiles']) for r in records)} perfis; {target}")


if __name__ == "__main__":
    acquire()
