from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class LLMResult:
    provider_id: str
    provider_name: str
    model: str
    content: str = ""
    latency_ms: int = 0
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    error: Optional[str] = None
    status: str = "ok"

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "provider_name": self.provider_name,
            "model": self.model,
            "content": self.content,
            "latency_ms": self.latency_ms,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "error": self.error,
            "status": self.status,
        }


@dataclass
class ProviderInfo:
    id: str
    name: str
    model: str
    family: str
    available: bool
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "family": self.family,
            "available": self.available,
            "description": self.description,
        }


class LLMProvider(ABC):
    id: str
    name: str
    model: str
    family: str
    description: str = ""

    @property
    @abstractmethod
    def available(self) -> bool:
        """True when credentials/config are present."""

    def info(self) -> ProviderInfo:
        return ProviderInfo(
            id=self.id,
            name=self.name,
            model=self.model,
            family=self.family,
            available=self.available,
            description=self.description,
        )

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        temperature: float = 0.4,
        max_tokens: int = 2048,
        timeout: float = 45.0,
    ) -> LLMResult:
        """Return a completed model response or raise on transport failure."""
