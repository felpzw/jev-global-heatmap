from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "src/app.py"


class AffinityAppTests(unittest.TestCase):
    def app(self):
        return AppTest.from_file(str(APP), default_timeout=15).run()

    def execute(self, app):
        next(b for b in app.button if b.label == "Calcular afinidade global").click().run()

    @patch("src.services.explanation_client.genai.Client")
    def test_confirmation_required_and_demo_no_credentials(self, client):
        app = self.app()
        self.execute(app)
        self.assertTrue(any("Confirme" in w.value for w in app.warning))
        self.assertNotIn("affinity_result", app.session_state)
        app.selectbox(key="dataset").select("Demonstração fictícia")
        app.checkbox(key="confirmed").check()
        self.execute(app)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get("plotly_chart")), 1)
        data = app.session_state["affinity_result"]["response"]
        self.assertEqual(len(data["countries"]), 195)
        self.assertEqual(data["metadata"]["dataset_version"], "synthetic-demo-v1")
        self.assertTrue(any("fictícios" in w.value for w in app.warning))
        client.assert_not_called()

    def test_rerun_preserves_result_figure_and_run_identity(self):
        app = self.app()
        app.checkbox(key="confirmed").check()
        self.execute(app)
        before = app.session_state["affinity_result"]["response"]
        spec = app.get("plotly_chart")[0].proto.spec
        app.text_input(key="country_search").set_value("VAT").run()
        self.assertEqual(app.session_state["affinity_result"]["response"], before)
        self.assertEqual(app.get("plotly_chart")[0].proto.spec, spec)
        self.assertEqual(app.dataframe[0].value.iloc[0]["ISO"], "VAT")
        self.assertFalse(app.exception)

    def test_changed_query_must_be_reinterpreted_and_keeps_old_result(self):
        app = self.app()
        app.checkbox(key="confirmed").check()
        self.execute(app)
        run_id = app.session_state["affinity_result"]["response"]["run_id"]
        app.text_area(key="context").set_value("praia e inglês")
        next(b for b in app.button if b.label == "Interpretar pedido").click().run()
        self.assertFalse(app.checkbox(key="confirmed").value)
        self.assertTrue(any("Praia" in w.value for w in app.warning))
        self.assertEqual(app.session_state["affinity_result"]["response"]["run_id"], run_id)
        self.assertFalse(app.exception)

    def test_only_requirements_invalid_and_previous_result_preserved(self):
        app = self.app()
        app.checkbox(key="confirmed").check()
        self.execute(app)
        run_id = app.session_state["affinity_result"]["response"]["run_id"]
        for attr in ["has_maritime_coast", "english_official"]:
            app.selectbox(key=f"role_{attr}").select("Obrigatório")
        self.execute(app)
        self.assertTrue(app.error)
        self.assertEqual(app.session_state["affinity_result"]["response"]["run_id"], run_id)
        self.assertFalse(app.exception)

    def test_example_negation_updates_review(self):
        app = self.app()
        app.selectbox(key="example").select("Interior · sem litoral")
        app.button(key="use_example").click().run()
        self.assertEqual(app.selectbox(key="expected_has_maritime_coast").value, "Não")
        self.assertEqual(app.selectbox(key="role_english_official").value, "Não usar")
        self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
