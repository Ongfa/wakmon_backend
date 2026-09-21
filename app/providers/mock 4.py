from __future__ import annotations

import asyncio
import time
from typing import Optional

from app.providers.base import LLMProvider, LLMResult


class MockProvider(LLMProvider):
    """Deterministic stand-in used when ORCHESTRATE_MOCK=true."""

    id = "mock"
    name = "Mock Analyst"
    family = "mock"
    description = "Local demo model — no API key required"
    model = "wakmon-mock-v1"

    def __init__(self, delay_s: float = 0.35) -> None:
        self.delay_s = delay_s

    @property
    def available(self) -> bool:
        return True

    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        temperature: float = 0.4,
        max_tokens: int = 2048,
        timeout: float = 45.0,
    ) -> LLMResult:
        started = time.perf_counter()
        await asyncio.sleep(self.delay_s)
        snippet = prompt.strip().replace("\n", " ")
        if len(snippet) > 160:
            snippet = snippet[:160] + "…"
        content = (
            "Mock council response (no live model key configured).\n\n"
            f"Prompt received: {snippet}\n\n"
            "View:\n"
            "- Treat this as a wiring check, not investment advice.\n"
            "- Add OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, GROQ_API_KEY, "
            "or MISTRAL_API_KEY to get real multi-model answers.\n"
            "- For Indian-market questions, compare valuation, cash flow quality, "
            "and values alignment before sizing a position."
        )
        return LLMResult(
            provider_id=self.id,
            provider_name=self.name,
            model=self.model,
            content=content,
            latency_ms=int((time.perf_counter() - started) * 1000),
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(content.split()),
        )
