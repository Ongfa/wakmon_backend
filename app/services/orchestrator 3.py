from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import AsyncIterator, Sequence
from typing import Optional

from app.core.config import settings
from app.providers.base import LLMProvider, LLMResult
from app.providers.registry import get_all_providers, get_available_providers

logger = logging.getLogger(__name__)

INVESTMENT_SYSTEM_PROMPT = """You are a research assistant for Wakmon, a values-based investing platform focused on the Indian market.

Guidelines:
- Be concise, specific, and honest about uncertainty.
- Weigh financial quality (cash flow, leverage, valuation) together with social impact (inclusion, labor, diversity, community).
- Use INR framing when discussing Indian companies.
- You are not a SEBI-registered advisor. Include a one-line disclaimer when the answer could be read as investment advice.
- Prefer short headings and bullet points for analytical questions.
"""

GENERAL_SYSTEM_PROMPT = """You are a helpful assistant for Wakmon users. Be clear, concise, and accurate. If you are unsure, say so."""

SYNTHESIS_SYSTEM_PROMPT = """You are the chair of Wakmon's AI council. Multiple models have independently answered the same user prompt.

Write a synthesis that:
1. States the consensus in 2-4 sentences.
2. Lists points of agreement.
3. Lists genuine disagreements or unique insights (name the model).
4. Ends with a practical takeaway for a values-based investor.
Keep the tone institutional, not hype. You are not a SEBI-registered advisor.
"""


class Orchestrator:
    def __init__(self, providers: Optional[Sequence[LLMProvider]] = None) -> None:
        self._providers = list(providers) if providers is not None else None
        self.timeout = settings.ORCHESTRATE_TIMEOUT_SECONDS

    def all_providers(self) -> list[LLMProvider]:
        if self._providers is not None:
            return list(self._providers)
        return get_all_providers()

    def available_providers(self, ids: Sequence[str] | None = None) -> list[LLMProvider]:
        if self._providers is not None:
            selected = {item.strip().lower() for item in ids} if ids else None
            providers = [p for p in self._providers if p.available]
            if selected:
                providers = [p for p in providers if p.id in selected]
            return providers
        return get_available_providers(ids)

    def resolve_system_prompt(self, mode: str, override: Optional[str]) -> str:
        if override and override.strip():
            return override.strip()
        if mode == "general":
            return GENERAL_SYSTEM_PROMPT
        return INVESTMENT_SYSTEM_PROMPT

    async def run(
        self,
        prompt: str,
        *,
        provider_ids: Sequence[str] | None = None,
        system_prompt: Optional[str] = None,
        mode: str = "investment",
        synthesize: bool = True,
        temperature: float = 0.4,
        max_tokens: int = 2048,
    ) -> dict:
        started = time.perf_counter()
        providers = self.available_providers(provider_ids)
        if not providers:
            raise LookupError("No LLM providers are configured or the requested models are unavailable.")

        system = self.resolve_system_prompt(mode, system_prompt)
        responses = await asyncio.gather(
            *[
                self._call_provider(
                    provider,
                    prompt,
                    system_prompt=system,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                for provider in providers
            ]
        )
        synthesis = None
        if synthesize:
            synthesis = await self._synthesize(
                prompt,
                list(responses),
                temperature=min(temperature, 0.4),
                max_tokens=max_tokens,
            )

        elapsed_ms = int((time.perf_counter() - started) * 1000)
        failed = sum(1 for item in responses if item.status != "ok")
        return {
            "prompt": prompt,
            "mode": mode,
            "responses": [item.to_dict() for item in responses],
            "synthesis": synthesis.to_dict() if synthesis else None,
            "elapsed_ms": elapsed_ms,
            "providers_used": len(responses) - failed,
            "providers_failed": failed,
        }

    async def run_stream(
        self,
        prompt: str,
        *,
        provider_ids: Sequence[str] | None = None,
        system_prompt: Optional[str] = None,
        mode: str = "investment",
        synthesize: bool = True,
        temperature: float = 0.4,
        max_tokens: int = 2048,
    ) -> AsyncIterator[tuple[str, dict]]:
        started = time.perf_counter()
        providers = self.available_providers(provider_ids)
        if not providers:
            yield (
                "error",
                {
                    "error": "No LLM providers are configured or the requested models are unavailable.",
                    "code": "no_providers",
                },
            )
            return

        system = self.resolve_system_prompt(mode, system_prompt)
        yield (
            "council_start",
            {
                "prompt": prompt,
                "mode": mode,
                "providers": [p.info().to_dict() for p in providers],
            },
        )

        tasks = [
            asyncio.create_task(
                self._call_provider(
                    provider,
                    prompt,
                    system_prompt=system,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            )
            for provider in providers
        ]
        for provider in providers:
            yield (
                "model_start",
                {"provider_id": provider.id, "provider_name": provider.name, "model": provider.model},
            )

        responses: list[LLMResult] = []
        for task in asyncio.as_completed(tasks):
            result = await task
            responses.append(result)
            event = "model_complete" if result.status == "ok" else "model_error"
            yield (event, result.to_dict())

        synthesis = None
        if synthesize:
            yield ("synthesis_start", {"provider_name": "Council chair"})
            synthesis = await self._synthesize(
                prompt,
                responses,
                temperature=min(temperature, 0.4),
                max_tokens=max_tokens,
            )
            event = "synthesis" if synthesis and synthesis.status == "ok" else "synthesis_error"
            yield (event, synthesis.to_dict() if synthesis else {"error": "Synthesis failed"})

        failed = sum(1 for item in responses if item.status != "ok")
        yield (
            "done",
            {
                "elapsed_ms": int((time.perf_counter() - started) * 1000),
                "providers_used": len(responses) - failed,
                "providers_failed": failed,
                "has_synthesis": bool(synthesis and synthesis.status == "ok"),
            },
        )

    async def _call_provider(
        self,
        provider: LLMProvider,
        prompt: str,
        *,
        system_prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> LLMResult:
        started = time.perf_counter()
        try:
            result = await asyncio.wait_for(
                provider.generate(
                    prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=self.timeout,
                ),
                timeout=self.timeout + 5,
            )
            if not result.latency_ms:
                result.latency_ms = int((time.perf_counter() - started) * 1000)
            if not result.content and not result.error:
                result.status = "error"
                result.error = "Empty model response"
            return result
        except asyncio.TimeoutError:
            logger.warning("Provider %s timed out", provider.id)
            return LLMResult(
                provider_id=provider.id,
                provider_name=provider.name,
                model=provider.model,
                status="error",
                error=f"Timed out after {self.timeout:.0f}s",
                latency_ms=int((time.perf_counter() - started) * 1000),
            )
        except Exception as exc:
            logger.warning("Provider %s failed: %s", provider.id, exc)
            return LLMResult(
                provider_id=provider.id,
                provider_name=provider.name,
                model=provider.model,
                status="error",
                error=str(exc),
                latency_ms=int((time.perf_counter() - started) * 1000),
            )

    async def _synthesize(
        self,
        prompt: str,
        responses: Sequence[LLMResult],
        *,
        temperature: float,
        max_tokens: int,
    ) -> Optional[LLMResult]:
        successful = [item for item in responses if item.status == "ok" and item.content]
        if not successful:
            return LLMResult(
                provider_id="synthesis",
                provider_name="Council chair",
                model="none",
                status="error",
                error="No successful model responses to synthesize.",
            )
        if len(successful) == 1:
            single = successful[0]
            return LLMResult(
                provider_id="synthesis",
                provider_name="Council chair",
                model=single.model,
                content=(
                    f"Only {single.provider_name} responded, so there is no multi-model consensus yet.\n\n"
                    f"{single.content}"
                ),
                status="ok",
            )

        chair = self._pick_chair(successful)
        if chair is None:
            return LLMResult(
                provider_id="synthesis",
                provider_name="Council chair",
                model="none",
                status="error",
                error="No available model to chair the synthesis.",
            )

        dossier = "\n\n".join(
            f"### {item.provider_name} ({item.model})\n{item.content}" for item in successful
        )
        synthesis_prompt = (
            f"User prompt:\n{prompt}\n\n"
            f"Independent model answers:\n{dossier}\n\n"
            "Produce the council synthesis now."
        )
        result = await self._call_provider(
            chair,
            synthesis_prompt,
            system_prompt=SYNTHESIS_SYSTEM_PROMPT,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        result.provider_id = "synthesis"
        result.provider_name = f"Council chair ({chair.name})"
        return result

    def _pick_chair(self, successful: Sequence[LLMResult]) -> Optional[LLMProvider]:
        preferred = (settings.ORCHESTRATE_SYNTHESIS_PROVIDER or "").strip().lower()
        available = self.available_providers()
        if not available:
            return None
        if preferred:
            for provider in available:
                if provider.id == preferred:
                    return provider
        # Prefer a model that already succeeded, then any available provider.
        succeeded_ids = {item.provider_id for item in successful}
        for provider in available:
            if provider.id in succeeded_ids:
                return provider
        return available[0]
