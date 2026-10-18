import math
import unittest

from evaluate_affinity import evaluate, percentile, ranking_metrics


class AffinityEvaluationTests(unittest.TestCase):
    def test_metrics_known_example_and_empty_relevance(self):
        result = ranking_metrics(["a", "b", "c"], ["a", "b"], {"a": 3, "c": 1}, 3)
        self.assertEqual(result["candidate_recall"], .5)
        self.assertEqual(result["precision_at_k"], 2/3)
        self.assertEqual(result["false_discards"], ["c"])
        self.assertAlmostEqual(result["ndcg_at_k"], 7.5 / (7 + 1 / math.log2(3)))
        self.assertIsNone(ranking_metrics([], [], {}, 3)["ndcg_at_k"])
        self.assertEqual(percentile([1, 2, 3], .5), 2)

    def test_reproducible_functional_gates_do_not_claim_live_results(self):
        report = evaluate(repeats=1)
        self.assertTrue(report["functional_gates_pass"])
        self.assertEqual(len(report["cases"]), 7)
        self.assertEqual(report["live"]["status"], "not_run")
        self.assertIsNone(report["live"]["cost_usd"])
        self.assertEqual(report["human_review"], "pending")


if __name__ == "__main__":
    unittest.main()
