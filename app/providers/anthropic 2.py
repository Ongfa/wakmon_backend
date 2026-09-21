from __future__ import annotations

import time
from typing import Optional

import httpx

from app.providers.base import LLMProvider, LLMResult


class AnthropicProvider(LLMProvider):
    id = "anthropic"
    name = "Claude"
    family = "anthropic"
    description = "Anthropic Claude — careful, long-context reasoning"

    def __init__(self, api_key: Optional[str], model: str) -> None:
        self.api_key = (api_key or "").strip()
        self.model = model

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        temperature: float = 0.4,
        max_tokens: int = 2048,
        timeout: float = 45.0,
    ) -> LLMResult:
        payload: dict = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            payload["system"] = system_prompt

        started = time.perf_counter()
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json=payload,
            )

        latency_ms = int((time.perf_counter() - started) * 1000)
        if response.status_code >= 400:
            detail = (response.text or "").strip().replace("\n", " ")[:400]
            raise RuntimeError(f"Claude HTTP {response.status_code}: {detail}")

        data = response.json()
        blocks = data.get("content") or []
        content = "".join(
            block.get("text", "") for block in blocks if isinstance(block, dict)
        ).strip()
        usage = data.get("usage") or {}
        return LLMResult(
            provider_id=self.id,
            provider_name=self.name,
            model=data.get("model") or self.model,
            content=content,
            latency_ms=latency_ms,
            prompt_tokens=usage.get("input_tokens"),
            completion_tokens=usage.get("output_tokens"),
        )
