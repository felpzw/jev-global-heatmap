from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "src/app.py"


class AffinityAppTests(unittest.TestCase):
    def app(self):
        return AppTest.from_file(str(APP), default_timeout=15).run()

    def execute(self, app):
        next(b for b in app.button if b.label == "Calculate global affinity").click().run()

    @patch("src.services.explanation_client.genai.Client")
    def test_confirmation_required_and_demo_no_credentials(self, client):
        app = self.app()
        self.execute(app)
        self.assertTrue(any("Confirm" in w.value for w in app.warning))
        self.assertNotIn("affinity_result", app.session_state)
        app.selectbox(key="dataset").select("Synthetic demonstration")
        app.checkbox(key="confirmed").check()
        self.execute(app)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get("plotly_chart")), 1)
        data = app.session_state["affinity_result"]["response"]
        self.assertEqual(len(data["countries"]), 195)
        self.assertEqual(data["metadata"]["dataset_version"], "synthetic-demo-v1")
        self.assertTrue(any("Synthetic" in w.value for w in app.warning))
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
        app.text_area(key="context").set_value("beaches and English")
        next(b for b in app.button if b.label == "Interpret request").click().run()
        self.assertFalse(app.checkbox(key="confirmed").value)
        self.assertTrue(any("Beaches" in w.value for w in app.warning))
        self.assertEqual(app.session_state["affinity_result"]["response"]["run_id"], run_id)
        self.assertFalse(app.exception)

    def test_only_requirements_invalid_and_previous_result_preserved(self):
        app = self.app()
        app.checkbox(key="confirmed").check()
        self.execute(app)
        run_id = app.session_state["affinity_result"]["response"]["run_id"]
        for attr in ["has_maritime_coast", "english_official"]:
            app.selectbox(key=f"role_{attr}").select("Required")
        self.execute(app)
        self.assertTrue(app.error)
        self.assertEqual(app.session_state["affinity_result"]["response"]["run_id"], run_id)
        self.assertFalse(app.exception)

    def test_example_negation_updates_review(self):
        app = self.app()
        app.selectbox(key="example").select("Inland · landlocked countries")
        app.button(key="use_example").click().run()
        self.assertEqual(app.selectbox(key="expected_has_maritime_coast").value, "No")
        self.assertEqual(app.selectbox(key="role_english_official").value, "Do not use")
        self.assertFalse(app.exception)

    def test_english_country_search_and_exported_explanation(self):
        app = self.app()
        self.assertEqual(app.title[0].value, "Connect an idea to the world.")
        app.checkbox(key="confirmed").check()
        self.execute(app)
        app.text_input(key="country_search").set_value("Germany").run()
        self.assertEqual(app.dataframe[0].value.iloc[0]["ISO"], "DEU")
        self.assertEqual(app.dataframe[0].value.iloc[0]["Country"], "Germany")
        data = app.session_state["affinity_result"]["response"]
        canada = next(c for c in data["countries"] if c["iso_alpha_3"] == "CAN")
        self.assertIn("Affinity ", canada["explanation"]["text"])
        self.assertIn("Derived from", canada["factors"][0]["evidence"]["reason"])
        self.assertFalse(app.exception)

    def test_portuguese_queries_are_still_supported_in_the_english_interface(self):
        app = self.app()
        app.text_area(key="context").set_value("Exijo litoral e prefiro inglês oficial")
        next(b for b in app.button if b.label == "Interpret request").click().run()
        self.assertEqual(app.selectbox(key="role_has_maritime_coast").value, "Required")
        self.assertEqual(app.selectbox(key="role_english_official").value, "Preference")
        app.checkbox(key="confirmed").check()
        self.execute(app)
        self.assertFalse(app.exception)

    def test_open_session_migrates_old_widget_labels_and_preserves_previous_result(self):
        original = self.app()
        original.checkbox(key="confirmed").check()
        self.execute(original)
        previous_result = original.session_state["affinity_result"]
        previous = previous_result["response"]["run_id"]
        # Seed the old session before building the new release's widget tree.
        app = AppTest.from_file(str(APP), default_timeout=15)
        app.session_state["affinity_result"] = previous_result
        app.session_state["ui_language"] = "pt"
        app.session_state["dataset"] = "Factbook · snapshot histórico"
        app.session_state["example"] = "Litoral + idioma · preferências"
        app.session_state["role_has_maritime_coast"] = "Preferência"
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["previous_language_result"]["response"]["run_id"], previous)
        self.assertEqual(app.selectbox(key="role_has_maritime_coast").value, "Preference")
        self.assertEqual(app.selectbox(key="dataset").value, "Factbook · historical snapshot")
        self.assertFalse(app.checkbox(key="confirmed").value)


if __name__ == "__main__":
    unittest.main()
