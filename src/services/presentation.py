"""English presentation of versioned evidence; source snapshots stay unchanged."""

PRESENTATION_VERSION = "en-v1"
EXPLANATION_PROMPT_VERSION = "evidence-only-en-v2"
CRITERION_LABELS = {"has_maritime_coast": "Maritime coastline", "english_official": "English as an official national language"}


def evidence_note(attribute_id: str, *, observed: bool) -> str:
    rule = (
        "Derived from Coastline: zero/landlocked means false; positive kilometres mean true. "
        "Lakes and the Caspian Sea do not count as maritime coastline."
        if attribute_id == "has_maritime_coast" else
        "Derived from Languages: explicitly official English means true; an official-language list "
        "without English means false; inconclusive national status remains missing."
    )
    return rule if observed else "The source does not establish this attribute at national level; no imputation. " + rule
