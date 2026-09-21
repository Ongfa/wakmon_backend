from __future__ import annotations

import time
from typing import Optional

import httpx

from app.providers.base import LLMProvider, LLMResult


class GeminiProvider(LLMProvider):
    id = "gemini"
    name = "Gemini"
    family = "google"
    description = "Google Gemini — fast multimodal reasoning"

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
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent"
        )
        payload: dict = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "thinkingConfig": {"thinkingBudget": 0},
            },
        }
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        started = time.perf_counter()
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                url,
                params={"key": self.api_key},
                headers={"Content-Type": "application/json"},
                json=payload,
            )

        latency_ms = int((time.perf_counter() - started) * 1000)
        if response.status_code >= 400:
            detail = (response.text or "").strip().replace("\n", " ")[:400]
            raise RuntimeError(f"Gemini HTTP {response.status_code}: {detail}")

        data = response.json()
        candidates = data.get("candidates") or []
        if not candidates:
            prompt_feedback = data.get("promptFeedback") or {}
            reason = prompt_feedback.get("blockReason") or "no candidates"
            raise RuntimeError(f"Gemini blocked or empty response: {reason}")

        parts = candidates[0].get("content", {}).get("parts") or []
        content = "".join(part.get("text", "") for part in parts if isinstance(part, dict)).strip()
        usage = data.get("usageMetadata") or {}
        return LLMResult(
            provider_id=self.id,
            provider_name=self.name,
            model=self.model,
            content=content,
            latency_ms=latency_ms,
            prompt_tokens=usage.get("promptTokenCount"),
            completion_tokens=usage.get("candidatesTokenCount"),
        )
