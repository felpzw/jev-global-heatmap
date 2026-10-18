"""Contratos de afinidade: nenhum SDK de LLM ou dependência de interface."""

import math
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator

from src.services.country_registry import COUNTRY_IDS

Attribute = Literal["has_maritime_coast", "english_official"]
CATALOG_VERSION = "coast-language-v1"
RANKER_VERSION = "weighted-boolean-v1"
SCHEMA_VERSION = "affinity-v1"


class Contract(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", str_strip_whitespace=True,
                              validate_assignment=True, allow_inf_nan=False,
                              revalidate_instances="always")


class Criterion(Contract):
    attribute_id: Attribute
    expected: bool = True
    role: Literal["requirement", "preference"] = "preference"
    weight: float = Field(default=1.0, gt=0, le=100)


class AffinityRequest(Contract):
    text: str = Field(min_length=1, max_length=4000)
    criteria: list[Criterion] = Field(min_length=1, max_length=2)
    confirmed: bool = False
    local_only: bool = True
    threshold: float = Field(default=50.0, ge=0, le=100)
    candidate_limit: int = Field(default=20, ge=1, le=20)
    explanation_limit: int = Field(default=10, ge=0, le=10)

    @model_validator(mode="after")
    def coherent(self):
        ids = [c.attribute_id for c in self.criteria]
        if len(set(ids)) != len(ids):
            raise ValueError("Critérios repetidos ou contraditórios.")
        if not any(c.role == "preference" for c in self.criteria):
            raise ValueError("Confirme pelo menos uma preferência para calcular afinidade.")
        if self.explanation_limit > self.candidate_limit:
            raise ValueError("Explicações não podem exceder o limite de candidatos.")
        return self


class CriterionEvidence(Contract):
    evidence_id: str = Field(min_length=1)
    iso_alpha_3: str
    attribute_id: Attribute
    value: bool | None
    data_status: Literal["observed", "missing", "conflicting", "not_applicable", "expired"]
    reason: str = Field(min_length=1)
    source_url: str | None = None
    source_file: str | None = None
    source_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    source_revision: str | None = None
    collected_at: str | None = None
    published_at: str | None = None
    reference_period: str | None = None
    license: str | None = None
    transformation: str = "factbook-extract-v1"

    @field_validator("iso_alpha_3")
    @classmethod
    def known(cls, value):
        if value not in COUNTRY_IDS:
            raise ValueError("País fora do registro.")
        return value

    @model_validator(mode="after")
    def admissible(self):
        if (self.data_status == "observed") != (self.value is not None):
            raise ValueError("Somente evidência observada pode ter valor booleano.")
        if self.data_status == "observed" and not all([
            self.source_url, self.source_file, self.source_sha256,
            self.source_revision, self.collected_at, self.license,
        ]):
            raise ValueError("Evidência observada requer proveniência completa.")
        return self


class AffinityFactor(Contract):
    criterion: Criterion
    evidence: CriterionEvidence
    normalized: float | None = Field(default=None, ge=0, le=1)
    contribution: float | None = Field(default=None, ge=0, le=100)

    @model_validator(mode="after")
    def calculated(self):
        if self.criterion.attribute_id != self.evidence.attribute_id:
            raise ValueError("Evidência de outro critério.")
        expected = (float(self.evidence.value == self.criterion.expected)
                    if self.evidence.data_status == "observed" else None)
        if self.normalized != expected:
            raise ValueError("Normalização incompatível com evidência.")
        contribution = (expected * self.criterion.weight if expected is not None
                        and self.criterion.role == "preference" else None)
        if self.contribution != contribution:
            raise ValueError("Contribuição incompatível com peso/papel.")
        return self


class CandidateExplanation(Contract):
    iso_alpha_3: str
    text: str = Field(min_length=1, max_length=900)
    evidence_ids: list[str] = Field(min_length=1, max_length=2)

    @field_validator("iso_alpha_3")
    @classmethod
    def known_country(cls, value):
        if value not in COUNTRY_IDS:
            raise ValueError("País fora do registro.")
        return value

    @field_validator("evidence_ids")
    @classmethod
    def unique_references(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("Referências duplicadas.")
        return value


class ExplanationBatch(Contract):
    explanations: list[CandidateExplanation] = Field(max_length=10)


class CountryAffinity(Contract):
    iso_alpha_3: str
    name: str = Field(min_length=1)
    status: Literal["ranked", "filtered_out", "insufficient_data", "error"]
    affinity_score: float | None = Field(default=None, ge=0, le=100)
    rank: int | None = Field(default=None, ge=1, le=195)
    reason: str = Field(min_length=1)
    factors: list[AffinityFactor]
    selection: Literal["selected", "not_selected", "not_eligible"] = "not_eligible"
    explanation_status: Literal["generated", "template", "not_requested", "error"] = "not_requested"
    explanation: CandidateExplanation | None = None
    explanation_source: Literal["gemini", "template"] | None = None

    @model_validator(mode="after")
    def consistent(self):
        if self.iso_alpha_3 not in COUNTRY_IDS:
            raise ValueError("País fora do registro.")
        if any(f.evidence.iso_alpha_3 != self.iso_alpha_3 for f in self.factors):
            raise ValueError("Evidência pertence a outro país.")
        if self.status == "ranked":
            if self.affinity_score is None or self.rank is None or self.selection == "not_eligible":
                raise ValueError("País ranked requer score, posição e seleção elegível.")
            if not self.factors or any(f.normalized is None for f in self.factors):
                raise ValueError("Ranking exige dados completos.")
            if any(f.normalized != 1 for f in self.factors if f.criterion.role == "requirement"):
                raise ValueError("País ranked viola requisito.")
            preferences = [f for f in self.factors if f.criterion.role == "preference"]
            if not preferences:
                raise ValueError("Ranking exige preferências.")
            score = 100 * sum(f.contribution for f in preferences) / sum(f.criterion.weight for f in preferences)
            if not math.isclose(score, self.affinity_score, abs_tol=1e-10):
                raise ValueError("Score incompatível com contribuições.")
        elif self.affinity_score is not None or self.rank is not None or self.selection != "not_eligible":
            raise ValueError("Estado sem ranking requer score/posição nulos e seleção inelegível.")
        if self.status == "filtered_out" and not any(
            f.criterion.role == "requirement" and f.normalized == 0 for f in self.factors
        ):
            raise ValueError("Exclusão exige evidência de requisito descumprido.")
        if self.status == "insufficient_data" and not any(f.normalized is None for f in self.factors):
            raise ValueError("Dados insuficientes exigem lacuna explícita.")
        if self.explanation_status == "not_requested":
            if self.explanation is not None or self.explanation_source is not None:
                raise ValueError("Explicação não solicitada deve ser nula.")
        else:
            if self.selection != "selected" or self.explanation is None:
                raise ValueError("Explicação exige país selecionado e texto validado.")
            source = "gemini" if self.explanation_status == "generated" else "template"
            if self.explanation_source != source or self.explanation.iso_alpha_3 != self.iso_alpha_3:
                raise ValueError("Origem ou país da explicação incompatível.")
            valid = {f.evidence.evidence_id for f in self.factors if f.normalized is not None}
            ids = self.explanation.evidence_ids
            if len(ids) != len(set(ids)) or not set(ids) <= valid:
                raise ValueError("Referências de explicação inválidas.")
        return self


class RunMetrics(Contract):
    calls: int = Field(default=0, ge=0, le=1)
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    cost_usd: float | None = Field(default=None, ge=0)
    ranking_ms: float = Field(default=0.0, ge=0)
    explanation_ms: float = Field(default=0.0, ge=0)
    cache_hit: bool = False


class RunMetadata(Contract):
    dataset_version: str
    dataset_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    catalog_version: Literal["coast-language-v1"] = CATALOG_VERSION
    registry_version: Literal["un-195-v1"] = "un-195-v1"
    ranker_version: Literal["weighted-boolean-v1"] = RANKER_VERSION
    schema_version: Literal["affinity-v1"] = SCHEMA_VERSION
    cache_key: str = Field(pattern=r"^[a-f0-9]{64}$")
    provider: str | None = None
    model: str | None = None
    prompt_version: str | None = None
    metrics: RunMetrics = Field(default_factory=RunMetrics)
    errors: list[str] = Field(default_factory=list)


class AffinityResponse(Contract):
    run_id: str
    status: Literal["completed", "partial"]
    request: AffinityRequest
    metadata: RunMetadata
    countries: list[CountryAffinity] = Field(min_length=195, max_length=195)
    candidate_ids: list[str] = Field(max_length=20)
    explanation_ids: list[str] = Field(max_length=10)

    @model_validator(mode="after")
    def reconciled(self):
        ids = [c.iso_alpha_3 for c in self.countries]
        if len(set(ids)) != 195 or set(ids) != COUNTRY_IDS:
            raise ValueError("Resultado deve representar exatamente o registro dos 195.")
        if not self.request.confirmed:
            raise ValueError("Pedido precisa ser confirmado antes da execução.")
        for c in self.countries:
            if [f.criterion for f in c.factors] != self.request.criteria:
                raise ValueError("Fatores diferem do pedido confirmado.")
        ranked = sorted((c for c in self.countries if c.status == "ranked"),
                        key=lambda c: (-c.affinity_score, c.iso_alpha_3))
        if [c.rank for c in ranked] != list(range(1, len(ranked) + 1)):
            raise ValueError("Ordem do ranking inválida.")
        expected = [c.iso_alpha_3 for c in ranked if c.affinity_score >= self.request.threshold][
            :self.request.candidate_limit]
        if self.candidate_ids != expected or self.explanation_ids != expected[:self.request.explanation_limit]:
            raise ValueError("Seleção difere do limiar/limites e da ordem do ranking.")
        for c in self.countries:
            if (c.selection == "selected") != (c.iso_alpha_3 in self.candidate_ids):
                raise ValueError("Seleção de país incompatível.")
            if (c.explanation_status != "not_requested") != (c.iso_alpha_3 in self.explanation_ids):
                raise ValueError("Explicações diferem do lote solicitado.")
        if self.request.local_only and (self.metadata.provider or self.metadata.metrics.calls):
            raise ValueError("local_only não permite chamadas externas.")
        if self.metadata.metrics.calls and not all([
            self.metadata.provider, self.metadata.model, self.metadata.prompt_version,
        ]):
            raise ValueError("Chamada LLM exige identificação de provedor/modelo/prompt.")
        partial = bool(self.metadata.errors) or any(
            c.status == "error" or c.explanation_status == "error" for c in self.countries)
        if (self.status == "partial") != partial:
            raise ValueError("Status da execução incompatível com falhas técnicas.")
        return self
