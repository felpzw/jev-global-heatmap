"""Registro de escopo ONU, independente de UI e de provedores de IA."""

import json
from pathlib import Path

REGISTRY_VERSION = "un-195-v1"
ROOT = Path(__file__).resolve().parents[2]
# Lista de escopo explícita: 193 membros + dois observadores. Não inclui dependências.
COUNTRY_IDS = frozenset("""
AFG ALB DZA AND AGO ATG ARG ARM AUS AUT AZE BHS BHR BGD BRB BLR BEL BLZ BEN
BTN BOL BIH BWA BRA BRN BGR BFA BDI CPV KHM CMR CAN CAF TCD CHL CHN COL COM
COG COD CRI CIV HRV CUB CYP CZE DNK DJI DMA DOM ECU EGY SLV GNQ ERI EST SWZ
ETH FJI FIN FRA GAB GMB GEO DEU GHA GRC GRD GTM GIN GNB GUY HTI HND HUN ISL
IND IDN IRN IRQ IRL ISR ITA JAM JPN JOR KAZ KEN KIR PRK KOR KWT KGZ LAO LVA
LBN LSO LBR LBY LIE LTU LUX MDG MWI MYS MDV MLI MLT MHL MRT MUS MEX FSM MDA
MCO MNG MNE MAR MOZ MMR NAM NRU NPL NLD NZL NIC NER NGA MKD NOR OMN PAK PLW
PAN PNG PRY PER PHL POL PRT QAT ROU RUS RWA KNA LCA VCT WSM SMR STP SAU SEN
SRB SYC SLE SGP SVK SVN SLB SOM ZAF SSD ESP LKA SDN SUR SWE CHE SYR TJK TZA
THA TLS TGO TON TTO TUN TUR TKM TUV UGA UKR ARE GBR USA URY UZB VUT VEN VNM
YEM ZMB ZWE VAT PSE
""".split())


def load_registry() -> list[dict]:
    data = json.loads((ROOT / "data/country_registry.json").read_text(encoding="utf-8"))
    countries = data["countries"]
    ids = [c["iso_alpha_3"] for c in countries]
    if (data["version"] != REGISTRY_VERSION or len(ids) != 195
            or set(ids) != COUNTRY_IDS or len(set(ids)) != len(ids)):
        raise ValueError("Registro deve representar exatamente os 195 Estados do escopo.")
    if any(not isinstance(c["m49"], str) or len(c["m49"]) != 3
           or not c["m49"].isdigit() for c in countries):
        raise ValueError("M49 deve ser uma string de três dígitos.")
    return countries
