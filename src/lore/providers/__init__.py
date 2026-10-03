"""The application-facing model boundary. SDK types stay in adapters."""
from typing import Protocol


class ProviderError(Exception):
    """A model configuration or request failure safe to show in the CLI."""


class ModelProvider(Protocol):
    def generate(self, prompt: str) -> str:
        """Return text for one prompt, or raise ProviderError."""
        ...


def create_provider(provider: str, model: str) -> ModelProvider:
    """Select an adapter explicitly; never fall back to another provider."""
    if provider not in {"gemini", "openrouter"}:
        raise ProviderError(f"Unsupported provider: {provider}. Choose openrouter or gemini.")
    if not model.strip():
        raise ProviderError("Specify a nonempty model with --model or LORE_MODEL.")
    if provider == "openrouter":
        from lore.providers.openrouter import OpenRouterProvider

        return OpenRouterProvider(model)
    from lore.providers.gemini import GeminiProvider

    return GeminiProvider(model)
