from pathlib import Path
import unittest
from unittest.mock import patch

from google.genai import types
from streamlit.testing.v1 import AppTest

from src.services.llm_client import ConfigurationError, InvalidResponseError, ProviderError
from src.services.schema import HeatmapResponse
from src.components.map_renderer import plot_heatmap
from tests.test_pipeline import VALID, completed_response

APP = Path(__file__).resolve().parents[1] / "src/app.py"


class AppTests(unittest.TestCase):
    def app(self):
        return AppTest.from_file(str(APP), default_timeout=15).run()

    def submit(self, app, context):
        app.text_area(key="context").set_value(context)
        next(button for button in app.button if button.label == "Gerar Mapeamento").click().run()

    @patch("src.services.llm_client.generate_heatmap")
    def test_blank_input_does_not_call_service(self, generate):
        app = self.app()
        self.submit(app, "  ")
        generate.assert_not_called()
        self.assertIn("Informe um contexto", app.warning[0].value)
        self.assertFalse(app.exception)

    @patch("src.services.llm_client.generate_heatmap")
    def test_success_persists_on_rerun_without_extra_calls(self, generate):
        generate.return_value = HeatmapResponse(countries=[VALID])
        app = self.app()
        self.submit(app, "Tema inicial")
        self.assertEqual(len(app.get("plotly_chart")), 1)
        app.text_area(key="context").set_value("Outro tema ainda não enviado").run()
        self.assertEqual(app.session_state["mapping"]["context"], "Tema inicial")
        self.assertEqual(len(app.get("plotly_chart")), 1)
        generate.assert_called_once_with("Tema inicial")
        self.assertFalse(app.exception)

    @patch("src.services.llm_client.generate_heatmap")
    def test_demo_works_without_credentials(self, generate):
        app = self.app()
        app.button(key="demo").click().run()
        self.assertEqual(app.session_state["mapping"]["source"], "demo")
        self.assertEqual(len(app.session_state["mapping"]["response"]["countries"]), 8)
        self.assertEqual(len(app.get("plotly_chart")), 1)
        self.assertIn("fictícios", app.warning[0].value)
        generate.assert_not_called()
        self.assertFalse(app.exception)

    @patch("src.components.map_renderer.plot_heatmap", wraps=plot_heatmap)
    @patch("src.services.llm_client.generate_heatmap")
    def test_rerun_reuses_figure_and_does_not_call_service(self, generate, render):
        app = self.app()
        app.button(key="demo").click().run()
        before = app.get("plotly_chart")[0].proto.spec
        app.run()
        self.assertEqual(app.get("plotly_chart")[0].proto.spec, before)
        render.assert_called_once()
        generate.assert_not_called()
        self.assertFalse(app.exception)

    @patch("src.services.llm_client.generate_heatmap")
    def test_failures_preserve_previous_result(self, generate):
        app = self.app()
        app.button(key="demo").click().run()
        for error in (ConfigurationError("Configure a chave."), ProviderError("Falha de conexão."),
                      InvalidResponseError("Resposta inválida.")):
            with self.subTest(error=type(error).__name__):
                generate.side_effect = error
                self.submit(app, "Novo tema")
                self.assertEqual(app.error[0].value, str(error))
                self.assertEqual(app.session_state["mapping"]["source"], "demo")
                self.assertEqual(len(app.get("plotly_chart")), 1)
                self.assertFalse(app.exception)

    @patch("src.services.llm_client.generate_heatmap")
    def test_empty_response_replaces_old_result_with_explanation(self, generate):
        generate.return_value = HeatmapResponse(countries=[])
        app = self.app()
        app.button(key="demo").click().run()
        self.submit(app, "Tema sem informações")
        self.assertEqual(len(app.get("plotly_chart")), 0)
        self.assertIn("Não há países", app.info[0].value)
        self.assertEqual(app.session_state["mapping"]["response"]["countries"], [])
        self.assertFalse(app.exception)

    @patch("src.services.llm_client.load_dotenv")
    @patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}, clear=True)
    @patch("src.services.llm_client.genai.Client")
    def test_interrupted_generation_preserves_previous_map(self, client_factory, _dotenv):
        response = completed_response(HeatmapResponse(countries=[VALID]).model_dump_json())
        response.candidates[0].finish_reason = types.FinishReason.MAX_TOKENS
        client = client_factory.return_value.__enter__.return_value
        client.models.generate_content.return_value = response
        app = self.app()
        app.button(key="demo").click().run()
        self.submit(app, "Pesquisa interrompida")
        self.assertIn("limite de geração", app.error[0].value)
        self.assertEqual(app.session_state["mapping"]["source"], "demo")
        self.assertEqual(len(app.get("plotly_chart")), 1)
        self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
