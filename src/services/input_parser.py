"""Conservative English/Portuguese catalog parser with explicit clarification."""

from dataclasses import dataclass, field
import re
import unicodedata

from src.services.affinity_schema import Criterion


def normalize(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text.lower())
                   if not unicodedata.combining(c))


@dataclass
class Interpretation:
    criteria: list[Criterion] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)


def interpret(text: str) -> Interpretation:
    result = Interpretation()
    value = re.sub(r"\b(don|doesn)['’]t\b", r"\1 not", normalize(text))
    if not value.strip() or len(text) > 4000:
        result.questions.append("Enter a request of up to 4,000 characters.")
        return result
    patterns = {
        "has_maritime_coast": r"\b(?:litoral(?: maritimo)?|costa maritima|(?:maritime )?coast(?:line|al)?|landlocked)\b",
        "english_official": (
            r"\b(?:ingles oficial(?: nacional)?|idioma oficial ingles|english official|official english|"
            r"english\s+(?:(?:as|is|being|must be)\s+)?(?:an?\s+|the\s+)?"
            r"(?:(?:national\s+)?official(?:\s+national)?\s+language))\b"
        ),
    }
    remaining = value
    for attr, pattern in patterns.items():
        matches = list(re.finditer(pattern, value))
        desired = []
        roles = []
        for match in matches:
            prefix = value[:match.start()]
            # Negação somente na mesma oração e próxima ao atributo.
            clause = re.split(r"[,;.!?]|\b(?:e|and|mas|but|or|ou)\b", prefix)[-1]
            negative = bool(re.search(r"\b(?:sem|nao|without|not|no|non)\b(?:[\s-]+\w+){0,3}[\s-]*$", clause))
            # Landlocked means the absence of maritime coastline; not landlocked reverses it.
            desired.append(negative if match.group() == "landlocked" else not negative)
            required = bool(re.search(
                r"\b(?:obrigatorio|exijo|exigir|precisa|deve|must|required|require|need)\b", clause))
            required = required or bool(re.search(r"\bmust\b", match.group())) or bool(re.match(
                r"\s+(?:is\s+)?required\b", value[match.end():]))
            roles.append("requirement" if required else "preference")
            if re.search(r"\b(?:not|nao)\s+(?:require|need|exigir)\b", clause):
                result.questions.append("Not requiring an attribute does not require its absence. Confirm the desired value and role.")
        if matches:
            if len(set(desired)) > 1:
                result.questions.append("The request contains conflicting criteria. Choose the intended value during review.")
            result.criteria.append(Criterion(attribute_id=attr, expected=desired[-1], role=roles[-1]))
            remaining = re.sub(pattern, " ", remaining)
    if re.search(r"\b(?:praia|praias|beach|beaches)\b", remaining):
        result.questions.append("Beaches are not the same as a coastline. Confirm whether maritime coastline is the criterion you want.")
    if re.search(r"\b(?:ingles|english|proficiencia)\b", remaining):
        result.questions.append("Confirm whether you mean English as an official national language; proficiency is outside this catalog.")
    if re.search(r"\b(?:or|ou)\b", value):
        result.questions.append("Alternative conditions need clarification. Active criteria are combined with AND.")
    # Remove apenas conectivos conhecidos. Não descarta silenciosamente objetivos novos.
    stopwords = r"\b(?:quero|busco|buscar|procuro|paises?|com|sem|e|ou|de|do|da|dos|das|o|a|os|as|um|uma|que|tenham|tem|tenha|preferir|prefiro|preferencia|obrigatorio|exijo|exigir|precisa|deve|nao|mais|por|favor|para|viajar|i|we|would|like|want|looking|look|for|country|countries|with|without|and|or|but|not|no|non|prefer|preference|must|required|require|need|have|has|a|an|the|that|are|is|be|do|does|don|doesn|please)\b"
    unknown = re.sub(stopwords, " ", remaining)
    unknown = re.sub(r"[^\w\s]", " ", unknown)
    if unknown.strip():
        result.questions.append("Terms outside the catalog: " + " ".join(unknown.split())[:160] + ". Review the scope before confirming.")
    if not result.criteria:
        result.questions.append("Select at least one supported preference during criteria review.")
    return result
