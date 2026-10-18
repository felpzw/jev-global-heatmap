import unittest

from src.components.affinity_map import plot_affinity_heatmap
from src.services.affinity_schema import Criterion
from src.services.evidence_service import load_demo_dataset
from src.services.jev_service import run_affinity
from tests.test_affinity import request


class AffinityMapTests(unittest.TestCase):
    def setUp(self):
        self.dataset = load_demo_dataset()

    def test_map_uses_affinity_zero_and_distinct_null_states(self):
        req = request(criteria=[Criterion(attribute_id="has_maritime_coast", role="requirement"),
                                Criterion(attribute_id="english_official")])
        result = run_affinity(req, dataset=self.dataset)
        figure = plot_affinity_heatmap(result)
        ranked = next(t for t in figure.data if t.coloraxis == "coloraxis")
        scores = dict(zip(ranked.locations, ranked.z))
        self.assertEqual(scores["BRA"], 0)
        self.assertNotIn("VAT", scores)
        self.assertEqual(figure.layout.coloraxis.cmin, 0)
        self.assertEqual(figure.layout.coloraxis.cmax, 100)
        self.assertIn("Insufficient data", [t.name for t in figure.data])

