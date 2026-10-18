"""SDK Gemini real sobre HTTP simulado: contrato, orçamento e geração completa."""

import json
import unittest
from unittest.mock import patch

from google import genai
import httpx

from src.services.evidence_service import load_demo_dataset
from src.services.explanation_client import ExplanationError, explain
from src.services.jev_service import run_affinity
from tests.test_affinity import request

REAL_CLIENT = genai.Client


@patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}, clear=True)
class ExplanationSDKTests(unittest.TestCase):
    def setUp(self):
        self.req = request(local_only=False, candidate_limit=2, explanation_limit=2)
        response = run_affinity(request(candidate_limit=2, explanation_limit=2), dataset=load_demo_dataset())
        by_iso = {c.iso_alpha_3: c for c in response.countries}
        self.selected = [by_iso[iso] for iso in response.explanation_ids]

    def payload(self, *, reason="STOP", change=None):
        body = {"explanations": [{"iso_alpha_3": c.iso_alpha_3, "text": "Explicação simulada.",
                                  "evidence_ids": [f.evidence.evidence_id for f in c.factors]}
                                 for c in self.selected]}
        if change:
            change(body)
        return {"candidates": [{"content": {"role": "model", "parts": [{"text": json.dumps(body)}]},
                                "finishReason": reason}],
                "usageMetadata": {"promptTokenCount": 123, "candidatesTokenCount": 45}}

    def call(self, payload):
        requests = []

        def respond(req):
            requests.append(req)
            return httpx.Response(200, json=payload)

        def factory(**kwargs):
            self.assertEqual(kwargs["http_options"].timeout, 30_000)
            self.assertEqual(kwargs["http_options"].retry_options.attempts, 1)
            kwargs["http_options"].httpx_client = httpx.Client(transport=httpx.MockTransport(respond))
            return REAL_CLIENT(**kwargs)

        with patch("src.services.explanation_client.genai.Client", side_effect=factory):
            result = explain(self.req, self.selected, model="test-model")
        return result, requests

    def test_only_requested_payload_no_raw_text_and_usage(self):
        result, requests = self.call(self.payload())
        self.assertEqual(len(requests), 1)
        body = json.loads(requests[0].content)
        config = body["generationConfig"]
        self.assertEqual(config["maxOutputTokens"], 4096)
        self.assertEqual(config["responseMimeType"], "application/json")
        self.assertIn("Explain in English", body["systemInstruction"]["parts"][0]["text"])
        payload = json.loads(body["contents"][0]["parts"][0]["text"])
        self.assertEqual([c["iso_alpha_3"] for c in payload["countries"]], ["CAN", "KEN"])
        self.assertNotIn("text", payload)
        self.assertNotIn("reason", json.dumps(payload))
        self.assertEqual(result.input_tokens, 123)
        self.assertEqual(result.output_tokens, 45)

    def test_truncation_block_and_invalid_lots(self):
        for reason in ["MAX_TOKENS", "SAFETY", "OTHER", None]:
            with self.subTest(reason=reason), self.assertRaises(ExplanationError):
                self.call(self.payload(reason=reason))
        with self.assertRaises(ExplanationError):
            self.call({"promptFeedback": {"blockReason": "SAFETY"}})
        for change in [lambda b: b["explanations"].reverse(),
                       lambda b: b["explanations"].pop(),
                       lambda b: b["explanations"].__setitem__(1, b["explanations"][0]),
                       lambda b: b["explanations"][0].update(iso_alpha_3="BRA"),
                       lambda b: b["explanations"][0].update(score=100),
                       lambda b: b["explanations"][0].update(evidence_ids=["wrong-id"])]:
            with self.subTest(change=change), self.assertRaises(ExplanationError):
                self.call(self.payload(change=change))

    def test_local_only_and_empty_never_call_provider(self):
        with patch("src.services.explanation_client.genai.Client") as client:
            with self.assertRaises(ExplanationError):
                explain(request(), self.selected, model="test")
            result = explain(self.req, [], model="test")
        self.assertEqual(result.batch.explanations, [])
        client.assert_not_called()


if __name__ == "__main__":
    unittest.main()
