from __future__ import annotations

from typing import Sequence

from app.core.config import settings
from app.providers.base import LLMProvider
from app.providers.gemini import GeminiProvider
from app.providers.mock import MockProvider
from app.providers.openai_compat import OpenAICompatProvider


def build_providers() -> list[LLMProvider]:
    """Construct Council providers. Availability depends on API keys."""
    providers: list[LLMProvider] = [
        GeminiProvider(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL),
        OpenAICompatProvider(
            provider_id="groq",
            name="Llama (Groq)",
            model=settings.GROQ_MODEL,
            family="meta",
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.GROQ_API_KEY,
            description="Groq-hosted GPT-OSS 120B (Llama 3.3 successor) — very low latency",
            extra_body={"reasoning_effort": "low"},
        ),
        OpenAICompatProvider(
            provider_id="mistral",
            name="Mistral AI",
            model=settings.MISTRAL_MODEL,
            family="mistral",
            base_url="https://api.mistral.ai/v1",
            api_key=settings.MISTRAL_API_KEY,
            description="Mistral AI — efficient European open-weight models",
        ),
    ]

    if settings.OLLAMA_ENABLED:
        providers.append(
            OpenAICompatProvider(
                provider_id="ollama",
                name="Ollama",
                model=settings.OLLAMA_MODEL,
                family="local",
                base_url=f"{settings.OLLAMA_BASE_URL.rstrip('/')}/v1",
                api_key=settings.OLLAMA_API_KEY or "ollama",
                description="Local Ollama model — runs on your machine",
                require_key=False,
            )
        )

    if settings.ORCHESTRATE_MOCK:
        providers.append(MockProvider())

    return providers


def get_all_providers() -> list[LLMProvider]:
    return build_providers()


def get_available_providers(ids: Sequence[str] | None = None) -> list[LLMProvider]:
    selected = {item.strip().lower() for item in ids} if ids else None
    providers = [p for p in get_all_providers() if p.available]
    if selected:
        providers = [p for p in providers if p.id in selected]
    return providers


def get_provider(provider_id: str) -> LLMProvider | None:
    needle = provider_id.strip().lower()
    for provider in get_all_providers():
        if provider.id == needle:
            return provider
    return None
