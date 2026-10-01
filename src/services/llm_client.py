"""Gemini Structured Outputs com validação local obrigatória."""

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from src.services.prompts import SYSTEM_PROMPT
from src.services.schema import HeatmapResponse

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = "gemini-3.5-flash-lite"
MAX_CONTEXT_LENGTH = 4000


class HeatmapError(Exception):
    """Erro seguro para exibir ao usuário, sem resposta bruta ou credenciais."""


class ConfigurationError(HeatmapError):
    pass


class ProviderError(HeatmapError):
    pass


class InvalidResponseError(HeatmapError):
    pass


def configured_model() -> str:
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    return os.getenv("GEMINI_MODEL", "").strip() or DEFAULT_MODEL


def parse_response(text: str | None) -> HeatmapResponse:
    if not text or not text.strip():
        raise InvalidResponseError("A IA não retornou dados. Reformule o contexto e tente novamente.")
    try:
        return HeatmapResponse.model_validate_json(text)
    except ValidationError:
        raise InvalidResponseError(
            "A resposta da IA contém JSON, países ou pontuações inválidos. Tente novamente."
        ) from None


def generate_heatmap(context: str, *, system_prompt: str = SYSTEM_PROMPT) -> HeatmapResponse:
    context = context.strip()
    if not context:
        raise HeatmapError("Informe um contexto de pesquisa antes de gerar o mapeamento.")
    if len(context) > MAX_CONTEXT_LENGTH:
        raise HeatmapError(f"Use até {MAX_CONTEXT_LENGTH} caracteres no contexto.")

    model = configured_model()
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key or not api_key.strip():
        raise ConfigurationError("Configure GEMINI_API_KEY no arquivo .env para usar a IA.")

    try:
        with genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=60_000, retry_options=types.HttpRetryOptions(attempts=1)
            ),
        ) as client:
            response = client.models.generate_content(
                model=model,
                contents=context,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_json_schema=HeatmapResponse.model_json_schema(),
                    max_output_tokens=8192,
                ),
            )
    except errors.APIError as error:
        if error.code in (401, 403):
            message = "A API recusou o acesso. Verifique a chave e as permissões do projeto."
        elif error.code == 429:
            message = "O limite de uso da API foi atingido. Aguarde e tente novamente."
        else:
            message = "Não foi possível consultar a IA. Verifique o modelo configurado e tente novamente."
        raise ProviderError(message) from None
    except (httpx.HTTPError, TimeoutError, ConnectionError):
        raise ProviderError("Falha de conexão ou tempo limite da IA. Tente novamente.") from None

    return parse_response(response.text)
