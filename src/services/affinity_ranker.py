"""Filtros e score determinístico puro, sem SDK de IA e sem chamadas externas."""

from src.services.affinity_schema import AffinityFactor, AffinityRequest, CountryAffinity
from src.services.evidence_service import Dataset
from src.services.country_registry import load_registry


class RunCancelled(Exception):
    """Cancelamento cooperativo; não publica uma resposta final incompleta."""


def rank_countries(request: AffinityRequest, dataset: Dataset, *, cancelled=lambda: False):
    if not request.confirmed:
        raise ValueError("Confirm the criteria before running the search.")
    rows = []
    for country in load_registry():
        if cancelled():
            raise RunCancelled("Search cancelled.")
        iso = country["iso_alpha_3"]
        factors = []
        for criterion in request.criteria:
            evidence = dataset.evidence[(iso, criterion.attribute_id)]
            value = float(evidence.value == criterion.expected) if evidence.data_status == "observed" else None
            factors.append(AffinityFactor(
                criterion=criterion, evidence=evidence, normalized=value,
                contribution=value * criterion.weight if value is not None and criterion.role == "preference" else None,
            ))
        failed = any(f.criterion.role == "requirement" and f.normalized == 0 for f in factors)
        missing = any(f.normalized is None for f in factors)
        if failed:
            status, reason, score = "filtered_out", "An observed value fails a required criterion.", None
        elif missing:
            status, reason, score = "insufficient_data", "Insufficient evidence for the active criteria.", None
        else:
            preferences = [f for f in factors if f.criterion.role == "preference"]
            score = 100 * sum(f.contribution for f in preferences) / sum(f.criterion.weight for f in preferences)
            status, reason = "ranked", "Affinity calculated from complete evidence for the active criteria."
        # Constrói a posição somente após ordenar todos os scores não arredondados.
        rows.append(dict(iso_alpha_3=iso, name=country["name_en"], status=status,
                         affinity_score=score, reason=reason, factors=factors,
                         rank=None, selection="not_eligible"))
    ranked = sorted((r for r in rows if r["status"] == "ranked"),
                    key=lambda r: (-r["affinity_score"], r["iso_alpha_3"]))
    candidates = [r["iso_alpha_3"] for r in ranked if r["affinity_score"] >= request.threshold][
        :request.candidate_limit]
    for position, row in enumerate(ranked, start=1):
        row["rank"] = position
        row["selection"] = "selected" if row["iso_alpha_3"] in candidates else "not_selected"
    return [CountryAffinity(**row) for row in rows], candidates
