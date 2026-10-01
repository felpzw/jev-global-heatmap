import json
import unittest
from unittest.mock import patch

from evaluate_prompts import CASES_PATH, evaluate_live, evaluate_offline
from src.services.llm_client import InvalidResponseError
from src.services.prompts import BASELINE_PROMPT, SYSTEM_PROMPT
from src.services.schema import HeatmapResponse


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))

    def test_offline_metrics_and_expected_rejection(self):
        records = evaluate_offline(self.cases)
        self.assertTrue(all(row["fixture_check_passed"] for row in records))
        self.assertEqual(records[0]["score_min"], 20)
        self.assertEqual(records[0]["score_max"], 90)
        self.assertEqual(records[1]["score_stddev"], 0)
        self.assertEqual(records[2]["countries"], 0)
        self.assertIsNone(records[2]["score_mean"])
        self.assertFalse(records[3]["validation_ok"])
        self.assertEqual(records[3]["iso_codes_valid"], 0)
        self.assertNotIn("end_to_end_seconds", records[0])

    @patch("evaluate_prompts.generate_heatmap")
    def test_live_comparison_keeps_response_and_alternates_order(self, generate):
        generate.return_value = HeatmapResponse.model_validate(self.cases[0]["response"])
        records = evaluate_live(self.cases, 2)
        self.assertEqual(len(records), 12)
        self.assertEqual(records[0]["prompt_variant"], "baseline")
        self.assertEqual(records[6]["prompt_variant"], "refined")
        self.assertEqual(records[0]["response"], generate.return_value.model_dump())
        self.assertEqual(generate.call_args_list[0].kwargs["system_prompt"], BASELINE_PROMPT)
        self.assertEqual(generate.call_args_list[1].kwargs["system_prompt"], SYSTEM_PROMPT)

    @patch("evaluate_prompts.generate_heatmap", side_effect=InvalidResponseError("Resposta inválida."))
    def test_live_failure_is_recorded_without_invented_metrics(self, generate):
        records = evaluate_live(self.cases[:1], 1)
        self.assertEqual(len(records), 2)
        self.assertFalse(records[0]["validation_ok"])
        self.assertNotIn("score_mean", records[0])
        self.assertNotIn("iso_codes_valid", records[0])


if __name__ == "__main__":
    unittest.main()
