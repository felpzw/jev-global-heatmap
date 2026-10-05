"""Integração com o SDK real e transporte HTTP simulado; nenhuma chamada externa."""

import json
import unittest
from unittest.mock import patch

import httpx
from google import genai

from src.services.llm_client import InvalidResponseError, generate_heatmap
from tests.test_pipeline import VALID

REAL_CLIENT = genai.Client


@patch("src.services.llm_client.load_dotenv")
@patch.dict("os.environ", {"GEMINI_API_KEY": "test-key", "GEMINI_MODEL": "test-model"}, clear=True)
class SDKIntegrationTests(unittest.TestCase):
    def request(self, payload):
        requests = []

        def respond(request):
            requests.append(request)
            return httpx.Response(200, json=payload)

        def client_factory(**kwargs):
            kwargs["http_options"].httpx_client = httpx.Client(transport=httpx.MockTransport(respond))
            return REAL_CLIENT(**kwargs)

        with patch("src.services.llm_client.genai.Client", side_effect=client_factory):
            result = generate_heatmap("Contexto de teste")
        return result, requests

    def payload(self, text=None, finish_reason="STOP"):
        if text is None:
            text = json.dumps({"countries": [VALID]})
        return {"candidates": [{"content": {"role": "model", "parts": [{"text": text}]},
                                "finishReason": finish_reason}]}

    def test_structured_request_and_validated_response(self, _dotenv):
        result, requests = self.request(self.payload())
        self.assertEqual(result.countries[0].iso_alpha_3, "BRA")
        self.assertEqual(len(requests), 1)
        request = requests[0]
        self.assertEqual(request.url.host, "generativelanguage.googleapis.com")
        self.assertTrue(request.url.path.endswith("/models/test-model:generateContent"))
        body = json.loads(request.content)
        self.assertEqual(body["generationConfig"]["responseMimeType"], "application/json")
        self.assertIn("countries", body["generationConfig"]["responseJsonSchema"]["properties"])
        self.assertEqual(body["contents"][0]["parts"][0]["text"], "Contexto de teste")

    def test_incomplete_generation_is_rejected_even_with_valid_json(self, _dotenv):
        for reason in ("MAX_TOKENS", "SAFETY", "OTHER", None):
            with self.subTest(reason=reason), self.assertRaises(InvalidResponseError):
                self.request(self.payload(finish_reason=reason))

    def test_prompt_block_has_an_actionable_message(self, _dotenv):
        with self.assertRaisesRegex(InvalidResponseError, "bloqueou"):
            self.request({"promptFeedback": {"blockReason": "SAFETY"}})

    def test_invalid_payload_is_rejected_after_sdk_decoding(self, _dotenv):
        for text in ("invalid-json", json.dumps({"countries": [{**VALID, "iso_alpha_3": "ZZZ"}]})):
            with self.subTest(text=text), self.assertRaises(InvalidResponseError):
                self.request(self.payload(text=text))

    def test_no_candidates_and_completed_empty_text_are_rejected(self, _dotenv):
        for payload in ({}, {"candidates": []}, self.payload(text="")):
            with self.subTest(payload=payload), self.assertRaises(InvalidResponseError):
                self.request(payload)

    def test_credentials_are_trimmed_and_blank_primary_uses_fallback(self, _dotenv):
        for primary, fallback, expected in (
            ("  test-key  ", "fallback-key", "test-key"),
            ("   ", "  fallback-key  ", "fallback-key"),
        ):
            with self.subTest(primary=primary), patch.dict(
                "os.environ", {"GEMINI_API_KEY": primary, "GOOGLE_API_KEY": fallback}
            ):
                _, requests = self.request(self.payload())
                self.assertEqual(requests[0].headers["x-goog-api-key"], expected)


if __name__ == "__main__":
    unittest.main()
