from __future__ import annotations

import json
import re
from typing import Any, Optional

from app.providers.base import LLMProvider
from app.providers.registry import get_available_providers

_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)
_JSON_RE = re.compile(r"(\{[\s\S]*\}|\[[\s\S]*\])")


def pick_provider(preferred: str = "gemini") -> LLMProvider:
    providers = get_available_providers()
    if not providers:
        raise LookupError("No LLM providers are configured on wakmon_backend.")
    needle = (preferred or "").strip().lower()
    if needle:
        for provider in providers:
            if provider.id == needle:
                return provider
    return providers[0]


def extract_json(text: str) -> Any:
    cleaned = _FENCE_RE.sub("", (text or "").strip()).strip()
    if not cleaned:
        raise ValueError("Model returned an empty response")
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = _JSON_RE.search(cleaned)
        if not match:
            raise ValueError("Model did not return JSON") from None
        return json.loads(match.group(1))


async def complete_json(
    provider: LLMProvider,
    *,
    prompt: str,
    system_prompt: str,
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> Any:
    result = await provider.generate(
        prompt,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    if result.status != "ok" or not result.content:
        raise RuntimeError(result.error or "Empty model response")
    return extract_json(result.content)
