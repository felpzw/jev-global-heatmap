from pathlib import Path
from html import unescape
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
        self.assertEqual(
            result.countries[0].context_summary,
            unescape(trace.customdata[0][0].replace("<br>", " ")),
        )
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

    def test_transparency_scale_and_revision(self):
        data = [{"iso_alpha_3": "BRA", "heat_score": 0, "context_summary": "Teste"}]
        figure = plot_heatmap(data)
        for background in (figure.layout.paper_bgcolor, figure.layout.plot_bgcolor,
                           figure.layout.geo.bgcolor):
            self.assertEqual(background, "rgba(0,0,0,0)")
        self.assertFalse(figure.layout.geo.showocean)
        self.assertEqual(figure.layout.coloraxis.colorbar.orientation, "h")
        self.assertEqual(list(figure.data[0].z), [0])
        self.assertEqual(figure.layout.uirevision, plot_heatmap(data).layout.uirevision)
        changed = [dict(data[0], heat_score=100)]
        self.assertNotEqual(figure.layout.uirevision, plot_heatmap(changed).layout.uirevision)
        self.assertEqual(figure.layout.transition.duration, 0)


if __name__ == "__main__":
    unittest.main()
