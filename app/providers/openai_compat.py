from __future__ import annotations

import time
from typing import Optional

import httpx

from app.providers.base import LLMProvider, LLMResult


class OpenAICompatProvider(LLMProvider):
    """OpenAI Chat Completions-compatible providers (OpenAI, Groq, Mistral, Ollama)."""

    def __init__(
        self,
        *,
        provider_id: str,
        name: str,
        model: str,
        family: str,
        base_url: str,
        api_key: Optional[str],
        description: str = "",
        extra_headers: Optional[dict[str, str]] = None,
        extra_body: Optional[dict] = None,
        require_key: bool = True,
    ) -> None:
        self.id = provider_id
        self.name = name
        self.model = model
        self.family = family
        self.description = description
        self.base_url = base_url.rstrip("/")
        self.api_key = (api_key or "").strip()
        self.extra_headers = extra_headers or {}
        self.extra_body = extra_body or {}
        self.require_key = require_key

    @property
    def available(self) -> bool:
        if not self.base_url:
            return False
        if self.require_key:
            return bool(self.api_key)
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
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Content-Type": "application/json",
            **self.extra_headers,
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **self.extra_body,
        }

        started = time.perf_counter()
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )

        latency_ms = int((time.perf_counter() - started) * 1000)
        if response.status_code >= 400:
            detail = _truncate(response.text)
            raise RuntimeError(f"{self.name} HTTP {response.status_code}: {detail}")

        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            raise RuntimeError(f"{self.name} returned no choices")

        content = (
            choices[0].get("message", {}).get("content")
            or choices[0].get("text")
            or ""
        )
        if isinstance(content, list):
            content = "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            )

        usage = data.get("usage") or {}
        return LLMResult(
            provider_id=self.id,
            provider_name=self.name,
            model=data.get("model") or self.model,
            content=str(content).strip(),
            latency_ms=latency_ms,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
        )


def _truncate(text: str, limit: int = 400) -> str:
    text = (text or "").strip().replace("\n", " ")
    return text if len(text) <= limit else text[:limit] + "…"
