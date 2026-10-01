from pathlib import Path
import unittest

from pydantic import ValidationError

from src.components.map_renderer import plot_heatmap
from src.services.schema import HeatmapResponse


class MapTests(unittest.TestCase):
    def test_demo_locations_colors_and_hover(self):
        result = HeatmapResponse.model_validate_json(
            (Path(__file__).resolve().parents[1] / "data/demo_heatmap.json").read_text()
        )
        figure = plot_heatmap(result.model_dump()["countries"])
        trace = figure.data[0]
        self.assertEqual(list(trace.locations), [c.iso_alpha_3 for c in result.countries])
        self.assertEqual(list(trace.z), [c.heat_score for c in result.countries])
        self.assertEqual(trace.locationmode, "ISO-3")
        self.assertIn("Contexto", trace.hovertemplate)
        self.assertIn(result.countries[0].context_summary, trace.customdata[0])
        self.assertEqual((figure.layout.coloraxis.cmin, figure.layout.coloraxis.cmax), (0, 100))
        self.assertIn('"type":"choropleth"', figure.to_json())

    def test_empty_and_invalid_data(self):
        self.assertEqual(len(plot_heatmap([]).data), 0)
        with self.assertRaises(ValidationError):
            plot_heatmap([{"iso_alpha_3": "ZZZ", "heat_score": 20, "context_summary": "Teste"}])

    def test_hover_escapes_html_without_mutating_input(self):
        data = [{"iso_alpha_3": "BRA", "heat_score": 0, "context_summary": "<b>Teste</b>"}]
        trace = plot_heatmap(data).data[0]
        self.assertIn("&lt;b&gt;Teste&lt;/b&gt;", trace.customdata[0])
        self.assertEqual(data[0]["context_summary"], "<b>Teste</b>")


if __name__ == "__main__":
    unittest.main()
