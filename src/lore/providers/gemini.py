"""Only this module depends on the Google SDK."""
import os

import httpx
from google import genai
from google.genai import errors, types

from lore.providers import ProviderError


class GeminiProvider:
    def __init__(self, model: str):
        self.model = model

    def generate(self, prompt: str) -> str:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ProviderError("Set GEMINI_API_KEY in your environment before calling Gemini.")
        try:
            # A single request, bounded in time and output. No automatic retries.
            with genai.Client(
                api_key=api_key,
                vertexai=False,
                http_options=types.HttpOptions(
                    timeout=60_000,
                    retry_options=types.HttpRetryOptions(attempts=1),
                ),
            ) as client:
                response = client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(max_output_tokens=1024),
                )
        except errors.APIError as exc:
            raise ProviderError(
                f"Gemini request failed (HTTP {exc.code}). Check your key, model, and quota."
            ) from None
        except httpx.TransportError:
            raise ProviderError("Could not reach Gemini. Check your connection and try again.") from None
        text = response.text
        if not text or not text.strip():
            raise ProviderError("Gemini returned no text (possibly blocked or output-limited).")
        return text
