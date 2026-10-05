import json
import unittest
from unittest.mock import patch

import httpx
from google.genai import errors, types
from pydantic import ValidationError

from src.services.llm_client import (
    ConfigurationError, HeatmapError, InvalidResponseError, ProviderError,
    generate_heatmap, parse_response,
)
from src.services.schema import CountryHeatmap, HeatmapResponse

VALID = {"iso_alpha_3": "BRA", "heat_score": 70, "context_summary": "Justificativa de teste."}


def completed_response(text):
    return types.GenerateContentResponse(candidates=[types.Candidate(
        content=types.Content(parts=[types.Part(text=text)]), finish_reason=types.FinishReason.STOP,
    )])


class SchemaTests(unittest.TestCase):
    def test_valid_json(self):
        result = parse_response(json.dumps({"countries": [VALID]}))
        self.assertEqual(result.countries[0].iso_alpha_3, "BRA")

    def test_rejects_invalid_values(self):
        for field, values in {
            "iso_alpha_3": ["ZZZ", "bra", "BR", "EU", "SUN", 123],
            "heat_score": [-1, 101, "70", True, float("nan"), float("inf")],
            "context_summary": ["", "  ", 123, "x" * 301],
        }.items():
            for value in values:
                with self.subTest(field=field, value=value), self.assertRaises(ValidationError):
                    CountryHeatmap.model_validate({**VALID, field: value})

    def test_boundaries_and_empty_result(self):
        for score in (0, 100):
            self.assertEqual(CountryHeatmap(**{**VALID, "heat_score": score}).heat_score, score)
        self.assertEqual(HeatmapResponse(countries=[]).countries, [])

    def test_rejects_duplicates_extra_keys_and_missing_fields(self):
        for data in (
            {"countries": [VALID, VALID]}, {"countries": [VALID], "extra": 1},
            {"countries": [{**VALID, "extra": 1}]}, {}, {"countries": [{"iso_alpha_3": "BRA"}]},
            [VALID], {"countries": [VALID] * 250},
        ):
            with self.subTest(data=str(data)[:80]), self.assertRaises(ValidationError):
                HeatmapResponse.model_validate(data)

    def test_rejects_bad_json_and_empty_text(self):
        for text in (None, "", " ", "not json", '```json\n{}\n```', '{"countries": null}'):
            with self.subTest(text=text), self.assertRaises(InvalidResponseError):
                parse_response(text)


@patch("src.services.llm_client.load_dotenv")
@patch.dict("os.environ", {"GEMINI_API_KEY": "test-key", "GEMINI_MODEL": "test-model"}, clear=True)
class ClientTests(unittest.TestCase):
    @patch("src.services.llm_client.genai.Client")
    def test_structured_request_is_validated(self, client_factory, _dotenv):
        client = client_factory.return_value.__enter__.return_value
        client.models.generate_content.return_value = completed_response(json.dumps({"countries": [VALID]}))
        self.assertEqual(len(generate_heatmap("  Teste  ").countries), 1)
        kwargs = client.models.generate_content.call_args.kwargs
        self.assertEqual(kwargs["contents"], "Teste")
        self.assertEqual(kwargs["model"], "test-model")
        self.assertEqual(kwargs["config"].response_json_schema, HeatmapResponse.model_json_schema())
        client.models.generate_content.return_value = completed_response('{"countries": [{"iso_alpha_3": "ZZZ"}]}')
        with self.assertRaises(InvalidResponseError):
            generate_heatmap("Teste")

    @patch("src.services.llm_client.genai.Client")
    def test_empty_and_long_input_never_call_api(self, client_factory, _dotenv):
        for context in (" ", "x" * 4001):
            with self.assertRaises(HeatmapError):
                generate_heatmap(context)
        client_factory.assert_not_called()

    @patch.dict("os.environ", {}, clear=True)
    @patch("src.services.llm_client.genai.Client")
    def test_missing_credentials(self, client_factory, _dotenv):
        with self.assertRaises(ConfigurationError):
            generate_heatmap("Teste")
        client_factory.assert_not_called()

    @patch("src.services.llm_client.genai.Client")
    def test_provider_errors_do_not_expose_secrets(self, client_factory, _dotenv):
        client = client_factory.return_value.__enter__.return_value
        for error in (errors.ClientError(429, {"message": "test-key"}),
                      errors.ClientError(403, {"message": "test-key"}),
                      errors.ServerError(500, {"message": "test-key"}),
                      httpx.ReadTimeout("test-key")):
            client.models.generate_content.side_effect = error
            with self.subTest(error=type(error).__name__), self.assertRaises(ProviderError) as caught:
                generate_heatmap("Teste")
            self.assertNotIn("test-key", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
