"""Orquestração JEV: ranking local, seleção, templates e explicação opcional."""

from hashlib import sha256
import json
import os
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from src.services.affinity_ranker import RunCancelled, rank_countries
from src.services.affinity_schema import (
    AffinityRequest, AffinityResponse, CATALOG_VERSION, CandidateExplanation,
    RANKER_VERSION, RunMetadata, CountryAffinity,
)
from src.services.evidence_service import Dataset, load_dataset

LABELS = {"has_maritime_coast": "litoral marítimo", "english_official": "inglês oficial nacional"}
PROMPT_VERSION = "evidence-only-v1"


def template(country, *, synthetic=False):
    factors = "; ".join(
        f"{LABELS[f.criterion.attribute_id]}: {'sim' if f.evidence.value else 'não'} "
        f"({'atende' if f.normalized else 'não atende'} ao critério, "
        f"{'obrigatório' if f.criterion.role == 'requirement' else f'peso {f.criterion.weight:g}'})"
        for f in country.factors)
    note = "Dados fictícios de demonstração." if synthetic else "Dados do snapshot histórico."
    return CandidateExplanation(iso_alpha_3=country.iso_alpha_3,
        text=f"Afinidade {country.affinity_score:.1f}/100. {factors}. {note}",
        evidence_ids=[f.evidence.evidence_id for f in country.factors])


def identity(request: AffinityRequest, dataset: Dataset, model: str | None):
    payload = {"request": request.model_dump(), "dataset": dataset.fingerprint,
               "ranker": RANKER_VERSION, "catalog": CATALOG_VERSION,
               "model": model, "prompt": PROMPT_VERSION, "limits": "1-call-4096-tokens-30s-v1"}
    return sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def save_checkpoint(path: Path, response: AffinityResponse, *, stage: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + str(uuid4()) + ".tmp")
    try:
        with temporary.open("w", encoding="utf-8") as stream:
            json.dump({"stage": stage, "response": response.model_dump()}, stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def run_affinity(request: AffinityRequest, *, dataset: Dataset | None = None,
                 cache: dict | None = None, checkpoint_dir: Path | None = None,
                 cancelled=lambda: False, progress=lambda message: None,
                 explanation_fn=None, model: str | None = None) -> AffinityResponse:
    # Revalida instâncias possivelmente alteradas fora do construtor.
    request = AffinityRequest.model_validate(request.model_dump())
    if not request.confirmed:
        raise ValueError("Confirme os critérios antes de executar.")
    if cancelled():
        raise RunCancelled("Execução cancelada.")
    dataset = dataset or load_dataset()
    if not request.local_only:
        from src.services.llm_client import configured_model
        model = model or configured_model()
    else:
        model = None
    key = identity(request, dataset, model)
    checkpoint = checkpoint_dir / f"{key}.json" if checkpoint_dir is not None else None
    cached = cache.get(key) if cache is not None else None
    stage = "final"
    if cached is None and checkpoint is not None and checkpoint.exists():
        try:
            saved = json.loads(checkpoint.read_text(encoding="utf-8"))
            stage, cached = saved["stage"], saved["response"]
        except (ValueError, KeyError):
            cached = None
    response = None
    if cached is not None:
        try:
            response = AffinityResponse.model_validate(cached)
            if (response.metadata.cache_key != key or response.request != request
                    or response.metadata.dataset_sha256 != dataset.fingerprint):
                response = None
        except ValueError:
            response = None
    if response is not None:
        response.metadata.metrics.cache_hit = True
        if stage == "final":
            progress("Resultado recuperado sem nova chamada.")
            return response
    else:
        progress("Aplicando critérios aos 195 Estados…")
        start = perf_counter()
        countries, candidates = rank_countries(request, dataset, cancelled=cancelled)
        explanation_ids = candidates[:request.explanation_limit]
        countries = [CountryAffinity.model_validate({
            **country.model_dump(), "explanation_status": "template", "explanation_source": "template",
            "explanation": template(country, synthetic=dataset.manifest.get("synthetic", False)).model_dump(),
        }) if country.iso_alpha_3 in explanation_ids else country for country in countries]
        response = AffinityResponse(
            run_id=str(uuid4()), status="completed", request=request,
            metadata=RunMetadata(dataset_version=dataset.version, dataset_sha256=dataset.fingerprint,
                                 cache_key=key),
            countries=countries, candidate_ids=candidates, explanation_ids=explanation_ids,
        )
        response.metadata.metrics.ranking_ms = (perf_counter() - start) * 1000
        if checkpoint is not None:
            save_checkpoint(checkpoint, response, stage="ranked")
    if cancelled():
        raise RunCancelled("Execução cancelada antes da explicação; ranking salvo para retomada.")
    if not request.local_only and response.explanation_ids:
        from src.services.explanation_client import explain, validate_batch
        has_key = bool(os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GOOGLE_API_KEY", "").strip())
        if has_key or explanation_fn is not None:
            progress(f"Explicando somente {len(response.explanation_ids)} selecionados…")
            selected = [{c.iso_alpha_3: c for c in response.countries}[iso] for iso in response.explanation_ids]
            response.metadata.provider = "gemini"
            response.metadata.model = model
            response.metadata.prompt_version = PROMPT_VERSION
            response.metadata.metrics.calls = 1
            start = perf_counter()
            try:
                # Cópia impede um adaptador externo de modificar o ranking por referência.
                result = (explanation_fn or explain)(request.model_copy(deep=True),
                    [c.model_copy(deep=True) for c in selected], model=model)
                batch = validate_batch(result.batch, selected)
                response.metadata.metrics.input_tokens = result.input_tokens
                response.metadata.metrics.output_tokens = result.output_tokens
                if cancelled():
                    raise RunCancelled("Execução cancelada; ranking salvo sem publicar a explicação.")
                updates = {e.iso_alpha_3: e for e in batch.explanations}
                response.countries = [CountryAffinity.model_validate({
                    **c.model_dump(), "explanation": updates[c.iso_alpha_3].model_dump(),
                    "explanation_status": "generated", "explanation_source": "gemini",
                }) if c.iso_alpha_3 in updates else c for c in response.countries]
            except RunCancelled:
                response.metadata.errors.append("Cancelado após envio ao provedor; templates e orçamento consumido preservados.")
                response.status = "partial"
                response.countries = [CountryAffinity.model_validate({
                    **c.model_dump(), "explanation_status": "error",
                }) if c.iso_alpha_3 in response.explanation_ids else c for c in response.countries]
                response.metadata.metrics.explanation_ms = (perf_counter() - start) * 1000
                if checkpoint is not None:
                    save_checkpoint(checkpoint, response, stage="final")
                raise
            except Exception:
                response.metadata.errors.append("Explicação indisponível ou inválida; templates preservados.")
                response.status = "partial"
                response.countries = [CountryAffinity.model_validate({
                    **c.model_dump(), "explanation_status": "error",
                }) if c.iso_alpha_3 in response.explanation_ids else c for c in response.countries]
            finally:
                response.metadata.metrics.explanation_ms = (perf_counter() - start) * 1000
        else:
            progress("Sem chave: justificativas locais por template.")
    if cancelled():
        raise RunCancelled("Execução cancelada.")
    response = AffinityResponse.model_validate(response.model_dump())
    if checkpoint is not None:
        save_checkpoint(checkpoint, response, stage="final")
    if cache is not None:
        cache[key] = response.model_dump()
        while len(cache) > 8:
            del cache[next(iter(cache))]
    progress("Concluído: mapa, ranking e evidências disponíveis.")
    return response
