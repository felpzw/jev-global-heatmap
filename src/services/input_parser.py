"""Parser conservador do catálogo; texto desconhecido exige revisão explícita."""

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
    value = normalize(text)
    if not value.strip() or len(text) > 4000:
        result.questions.append("Informe um pedido de até 4000 caracteres.")
        return result
    patterns = {
        "has_maritime_coast": r"\b(?:litoral(?: maritimo)?|costa maritima|coast(?:line)?)\b",
        "english_official": r"\b(?:ingles oficial(?: nacional)?|idioma oficial ingles|english official|official english)\b",
    }
    remaining = value
    for attr, pattern in patterns.items():
        matches = list(re.finditer(pattern, value))
        desired = []
        roles = []
        for match in matches:
            prefix = value[:match.start()]
            # Negação somente na mesma oração e próxima ao atributo.
            clause = re.split(r"[,;.!?]|\b(?:e|and|mas)\b", prefix)[-1]
            negative = bool(re.search(r"\b(?:sem|nao|without|not|no)\b(?:\s+\w+){0,3}\s*$", clause))
            desired.append(not negative)
            roles.append("requirement" if re.search(
                r"\b(?:obrigatorio|exijo|exigir|precisa|deve|must|required)\b", clause) else "preference")
        if matches:
            if len(set(desired)) > 1:
                result.questions.append("Há critérios contraditórios. Escolha a opção desejada na revisão.")
            result.criteria.append(Criterion(attribute_id=attr, expected=desired[-1], role=roles[-1]))
            remaining = re.sub(pattern, " ", remaining)
    if re.search(r"\b(?:praia|praias|beach|beaches)\b", remaining):
        result.questions.append("Praia não equivale a litoral. Confirme se deseja usar apenas presença de litoral marítimo.")
    if re.search(r"\b(?:ingles|english|proficiencia)\b", remaining):
        result.questions.append("Confirme se deseja status oficial nacional do inglês; proficiência não está no catálogo.")
    # Remove apenas conectivos conhecidos. Não descarta silenciosamente objetivos novos.
    stopwords = r"\b(?:quero|busco|buscar|procuro|paises?|com|sem|e|ou|de|do|da|dos|das|o|a|os|as|um|uma|que|tenham|tem|tenha|preferir|prefiro|preferencia|obrigatorio|exijo|exigir|precisa|deve|nao|mais|por|favor|para|viajar|countries|with|without|and|or|not|no|prefer|must|required)\b"
    unknown = re.sub(stopwords, " ", remaining)
    unknown = re.sub(r"[^\w\s]", " ", unknown)
    if unknown.strip():
        result.questions.append("Termos fora do catálogo: " + " ".join(unknown.split())[:160] + ". Revise o escopo antes de confirmar.")
    if not result.criteria:
        result.questions.append("Selecione pelo menos uma preferência suportada na revisão dos critérios.")
    return result
