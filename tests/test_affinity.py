from dataclasses import replace
import json
from pathlib import Path
import tempfile
from threading import Event
import unittest
from unittest.mock import Mock, patch

from pydantic import ValidationError

from src.services.affinity_ranker import RunCancelled
from src.services.affinity_schema import (
    AffinityRequest, AffinityResponse, CandidateExplanation, Criterion, ExplanationBatch,
)
from src.services.country_registry import COUNTRY_IDS, load_registry
from src.services.evidence_service import load_dataset, load_demo_dataset
from src.services.explanation_client import ExplanationResult, validate_batch
from src.services.input_parser import interpret
from src.services.jev_service import identity, run_affinity


def request(**kwargs):
    values = dict(text="Prefiro litoral e inglês oficial", confirmed=True,
        criteria=[Criterion(attribute_id="has_maritime_coast", weight=3.0),
                  Criterion(attribute_id="english_official", weight=1.0)])
    return AffinityRequest(**(values | kwargs))


def fake_explain(req, countries, *, model):
    return ExplanationResult(ExplanationBatch(explanations=[
        CandidateExplanation(iso_alpha_3=c.iso_alpha_3, text="Justificativa simulada para teste de integração.",
                             evidence_ids=[f.evidence.evidence_id for f in c.factors])
        for c in countries]), input_tokens=123, output_tokens=45)


class FoundationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_affinity(request(), dataset=load_demo_dataset())

    def test_exact_registry_and_m49(self):
        rows = load_registry()
        self.assertEqual(len(rows), 195)
        self.assertEqual({r["iso_alpha_3"] for r in rows}, COUNTRY_IDS)
        self.assertEqual(sum(r["un_status"] == "member" for r in rows), 193)
        self.assertEqual({r["iso_alpha_3"] for r in rows if r["un_status"] == "observer"}, {"VAT", "PSE"})
        self.assertEqual(next(r["m49"] for r in rows if r["iso_alpha_3"] == "AFG"), "004")

    def test_json_roundtrip(self):
        self.assertEqual(AffinityResponse.model_validate_json(self.result.model_dump_json()), self.result)

    def test_bad_weights_and_types(self):
        for bad in [0, -1, float("nan"), float("inf"), True, "1"]:
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                Criterion(attribute_id="has_maritime_coast", weight=bad)
        with self.assertRaises(ValidationError):
            Criterion(attribute_id="english_official", expected="true")
        with self.assertRaises(ValidationError):
            Criterion(attribute_id="invented")

    def test_duplicate_all_requirement_and_limits_rejected(self):
        invalid = [dict(criteria=[Criterion(attribute_id="has_maritime_coast")] * 2),
                   dict(criteria=[Criterion(attribute_id="has_maritime_coast", role="requirement")]),
                   dict(candidate_limit=2), dict(explanation_limit=11), dict(threshold=float("nan"))]
        for values in invalid:
            with self.subTest(values=values), self.assertRaises(ValidationError):
                request(**values)

    def test_exact_195_cannot_hide_duplicate_missing_or_extra(self):
        data = self.result.model_dump()
        for mutate in [lambda d: d["countries"].pop(),
                       lambda d: d["countries"].__setitem__(1, d["countries"][0]),
                       lambda d: d["countries"][0].__setitem__("iso_alpha_3", "ATA")]:
            changed = json.loads(json.dumps(data))
            mutate(changed)
            with self.assertRaises(ValidationError):
                AffinityResponse.model_validate(changed)

    def test_invalid_score_status_and_selection_rejected(self):
        for mutation in [dict(affinity_score=float("nan")), dict(affinity_score=float("inf")),
                         dict(affinity_score=101.0), dict(affinity_score=12.0),
                         dict(status="filtered_out"), dict(rank=195)]:
            data = self.result.model_dump()
            country = next(c for c in data["countries"] if c["iso_alpha_3"] == "CAN")
            country.update(mutation)
            with self.subTest(mutation=mutation), self.assertRaises(ValidationError):
                AffinityResponse.model_validate(data)
        data = self.result.model_dump()
        data["candidate_ids"].reverse()
        with self.assertRaises(ValidationError):
            AffinityResponse.model_validate(data)


class ParserTests(unittest.TestCase):
    def test_natural_english_requests_and_landlocked_negation(self):
        combinations = [
            ("I prefer countries with a coastline and English as an official language",
             [(True, "preference"), (True, "preference")]),
            ("I require a coastline and prefer English as an official language",
             [(True, "requirement"), (True, "preference")]),
            ("A coastline is required and I prefer official English",
             [(True, "requirement"), (True, "preference")]),
            ("I prefer landlocked countries", [(False, "preference")]),
            ("I prefer countries that are not landlocked", [(True, "preference")]),
            ("I prefer countries that don't have a coastline", [(False, "preference")]),
            ("I prefer non-coastal countries", [(False, "preference")]),
        ]
        for text, expected in combinations:
            with self.subTest(text=text):
                parsed = interpret(text)
                self.assertFalse(parsed.questions)
                self.assertEqual([(c.expected, c.role) for c in parsed.criteria], expected)

    def test_english_ambiguity_disjunction_and_negated_requirement_need_review(self):
        for text in ["I want beaches and English", "I prefer a coastline and safety",
                     "A coastline or official English", "I do not require a coastline",
                     "I prefer a coastline and landlocked countries"]:
            with self.subTest(text=text):
                self.assertTrue(interpret(text).questions)

    def test_supported_combination_negation_and_requirements(self):
        parsed = interpret("Exijo litoral e prefiro inglês oficial")
        self.assertFalse(parsed.questions)
        self.assertEqual([c.role for c in parsed.criteria], ["requirement", "preference"])
        for text in ["Prefiro países sem litoral", "Prefiro países que não tenham litoral"]:
            self.assertFalse(interpret(text).criteria[0].expected)
        self.assertTrue(interpret("países sem litoral e inglês oficial").criteria[1].expected)

    def test_ambiguous_unsupported_and_contradictory_not_silent(self):
        for text in ["Quero praia e inglês", "litoral e segurança", "litoral e sem litoral", "", "x" * 4001]:
            with self.subTest(text=text[:50]):
                self.assertTrue(interpret(text).questions)


class RankingTests(unittest.TestCase):
    def setUp(self):
        self.dataset = load_demo_dataset()

    def test_weighted_scores_stable_ties_and_missing(self):
        result = run_affinity(request(), dataset=self.dataset)
        countries = {c.iso_alpha_3: c for c in result.countries}
        self.assertEqual(result.candidate_ids, ["CAN", "KEN", "BRA", "MEX"])
        self.assertEqual([countries[i].affinity_score for i in ["CAN", "BRA", "CHE"]], [100, 75, 0])
        self.assertEqual(countries["CHE"].status, "ranked")
        self.assertEqual(countries["PSE"].status, "insufficient_data")
        self.assertIsNone(countries["PSE"].affinity_score)
        self.assertEqual(result, AffinityResponse.model_validate(result.model_dump()))

    def test_english_names_explanations_and_evidence_preserve_snapshot_values(self):
        data = load_dataset()
        result = run_affinity(request(text="I prefer a coastline and official English"), dataset=data)
        countries = {c.iso_alpha_3: c for c in result.countries}
        self.assertEqual(countries["DEU"].name, "Germany")
        self.assertIn("complete evidence", countries["CAN"].reason)
        self.assertTrue(countries["CAN"].explanation.text.startswith("Affinity "))
        self.assertIn("Historical snapshot data", countries["CAN"].explanation.text)
        self.assertEqual(result.metadata.presentation_version, "en-v1")
        source = Path(__file__).resolve().parents[1] / "data/affinity/v1/evidence.jsonl"
        for line in source.read_text().splitlines():
            original = json.loads(line)
            current = data.evidence[(original["iso_alpha_3"], original["attribute_id"])]
            self.assertEqual(current.value, original["value"])
            self.assertEqual(current.source_sha256, original["source_sha256"])
            self.assertIn("Derived from", current.reason)

    def test_language_version_invalidates_previous_cached_explanations(self):
        req = request()
        current = identity(req, self.dataset, None)
        with patch("src.services.jev_service.PRESENTATION_VERSION", "pt-v0"):
            previous = identity(req, self.dataset, None)
        self.assertNotEqual(current, previous)

    def test_known_failure_overrides_missing_requirement_unknown_does_not_exclude(self):
        req = request(criteria=[Criterion(attribute_id="has_maritime_coast", role="requirement"),
                                Criterion(attribute_id="english_official")])
        countries = {c.iso_alpha_3: c for c in run_affinity(req, dataset=self.dataset).countries}
        self.assertEqual(countries["VAT"].status, "filtered_out")
        self.assertEqual(countries["AFG"].status, "insufficient_data")
        self.assertEqual(countries["BRA"].affinity_score, 0)

    def test_confirmed_required(self):
        with self.assertRaises(ValueError):
            run_affinity(request(confirmed=False), dataset=self.dataset)

    @patch("socket.socket.connect", side_effect=AssertionError("Network forbidden"))
    @patch("src.services.explanation_client.genai.Client")
    def test_local_only_does_not_use_network_even_with_key(self, client, connect):
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test"}):
            result = run_affinity(request(), dataset=self.dataset)
        client.assert_not_called()
        connect.assert_not_called()
        self.assertEqual(result.metadata.metrics.calls, 0)
        self.assertTrue(all(c.explanation_source == "template" for c in result.countries if c.explanation))

    def test_empty_selection_does_not_call_llm_or_fill_top_k(self):
        explain = Mock(side_effect=AssertionError("Must not call"))
        req = request(local_only=False, threshold=1.0, criteria=[
            Criterion(attribute_id="has_maritime_coast", expected=False),
            Criterion(attribute_id="english_official", role="requirement")])
        result = run_affinity(req, dataset=self.dataset, explanation_fn=explain)
        self.assertEqual(result.candidate_ids, [])
        explain.assert_not_called()

    def test_only_selected_sent_scores_unchanged_and_metadata(self):
        explain = Mock(side_effect=fake_explain)
        req = request(local_only=False, candidate_limit=3, explanation_limit=2)
        result = run_affinity(req, dataset=self.dataset, explanation_fn=explain, model="test-model")
        selected = explain.call_args.args[1]
        self.assertEqual([c.iso_alpha_3 for c in selected], ["CAN", "KEN"])
        self.assertEqual(result.explanation_ids, ["CAN", "KEN"])
        self.assertEqual(result.metadata.metrics.input_tokens, 123)
        self.assertEqual(result.metadata.metrics.calls, 1)
        self.assertEqual(result.metadata.model, "test-model")
        self.assertIsNone(result.metadata.metrics.cost_usd)
        baseline = run_affinity(request(), dataset=self.dataset)
        self.assertEqual([(c.iso_alpha_3, c.affinity_score) for c in result.countries],
                         [(c.iso_alpha_3, c.affinity_score) for c in baseline.countries])

    def test_provider_failure_and_bad_reference_preserve_ranking(self):
        def invalid(req, countries, *, model):
            result = fake_explain(req, countries, model=model)
            result.batch.explanations[0].evidence_ids = ["injected:reference"]
            return result
        for explain in [Mock(side_effect=TimeoutError), invalid]:
            result = run_affinity(request(local_only=False), dataset=self.dataset, explanation_fn=explain)
            self.assertEqual(result.status, "partial")
            self.assertEqual(result.candidate_ids, ["CAN", "KEN", "BRA", "MEX"])
            self.assertTrue(all(c.explanation_source == "template" and c.explanation_status == "error"
                                for c in result.countries if c.explanation))

    def test_no_key_uses_templates_without_provider_metadata(self):
        with patch.dict("os.environ", {}, clear=True), patch("src.services.llm_client.load_dotenv"):
            result = run_affinity(request(local_only=False), dataset=self.dataset)
        self.assertIsNone(result.metadata.provider)
        self.assertEqual(result.metadata.metrics.calls, 0)

    def test_cache_identity_and_isolation(self):
        cache = {}
        explain = Mock(side_effect=fake_explain)
        req = request(local_only=False)
        first = run_affinity(req, dataset=self.dataset, cache=cache, explanation_fn=explain, model="test")
        second = run_affinity(req, dataset=self.dataset, cache=cache, explanation_fn=explain, model="test")
        self.assertEqual(first.run_id, second.run_id)
        self.assertTrue(second.metadata.metrics.cache_hit)
        self.assertEqual(explain.call_count, 1)
        self.assertNotEqual(identity(req, self.dataset, "test"), identity(req, self.dataset, "other"))
        self.assertNotEqual(identity(req, self.dataset, "test"),
                            identity(req, replace(self.dataset, fingerprint="other"), "test"))
        third = run_affinity(req, dataset=self.dataset, cache={}, explanation_fn=explain, model="test")
        self.assertNotEqual(third.run_id, first.run_id)
        self.assertEqual(explain.call_count, 2)

    def test_atomic_checkpoint_resume_and_cancel(self):
        with tempfile.TemporaryDirectory() as folder:
            checkpoint = Path(folder)
            first = run_affinity(request(), dataset=self.dataset, checkpoint_dir=checkpoint)
            second = run_affinity(request(), dataset=self.dataset, checkpoint_dir=checkpoint)
            self.assertEqual(first.run_id, second.run_id)
            self.assertTrue(second.metadata.metrics.cache_hit)
            self.assertEqual(len(list(checkpoint.glob("*.json"))), 1)
            self.assertFalse(list(checkpoint.glob("*.tmp")))
        with self.assertRaises(RunCancelled):
            run_affinity(request(), dataset=self.dataset, cancelled=lambda: True)

    def test_cancel_after_ranking_resumes_pending_explanation(self):
        with tempfile.TemporaryDirectory() as folder:
            checks = Mock(side_effect=[False] * 196 + [True])
            req = request(local_only=False)
            with self.assertRaises(RunCancelled):
                run_affinity(req, dataset=self.dataset, checkpoint_dir=Path(folder), cancelled=checks,
                             explanation_fn=fake_explain, model="test")
            result = run_affinity(req, dataset=self.dataset, checkpoint_dir=Path(folder),
                                  explanation_fn=fake_explain, model="test")
            self.assertTrue(result.metadata.metrics.cache_hit)
            self.assertEqual(result.metadata.metrics.calls, 1)
            self.assertTrue(all(c.explanation_status == "generated" for c in result.countries if c.explanation))

    def test_cancel_after_provider_preserves_consumed_budget_in_checkpoint(self):
        event = Event()

        def provider(req, countries, *, model):
            event.set()
            return fake_explain(req, countries, model=model)

        with tempfile.TemporaryDirectory() as folder:
            req = request(local_only=False)
            with self.assertRaises(RunCancelled):
                run_affinity(req, dataset=self.dataset, checkpoint_dir=Path(folder),
                             cancelled=event.is_set, explanation_fn=provider, model="test")
            should_not_call = Mock(side_effect=AssertionError("Budget already consumed"))
            resumed = run_affinity(req, dataset=self.dataset, checkpoint_dir=Path(folder),
                                   explanation_fn=should_not_call, model="test")
            should_not_call.assert_not_called()
            self.assertEqual(resumed.status, "partial")
            self.assertEqual(resumed.metadata.metrics.calls, 1)
            self.assertEqual(resumed.metadata.metrics.input_tokens, 123)

    def test_dataset_integrity_and_real_coverage(self):
        real = load_dataset()
        self.assertEqual(len(real.evidence), 390)
        self.assertEqual(sum(e.value is not None for e in real.evidence.values() if e.attribute_id == "has_maritime_coast"), 195)
        self.assertFalse(real.evidence[("KAZ", "has_maritime_coast")].value)
        self.assertFalse(real.evidence[("AZE", "has_maritime_coast")].value)
        self.assertTrue(real.evidence[("PSE", "has_maritime_coast")].value)
        self.assertEqual(real.evidence[("JPN", "english_official")].data_status, "missing")



if __name__ == "__main__":
    unittest.main()
