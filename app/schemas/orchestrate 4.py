from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class OrchestrateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=12000)
    system_prompt: Optional[str] = Field(None, max_length=8000)
    providers: Optional[List[str]] = None
    synthesize: bool = True
    temperature: float = Field(0.4, ge=0, le=2)
    max_tokens: int = Field(2048, ge=64, le=8192)
    mode: Literal["investment", "general"] = "investment"

    @field_validator("prompt")
    @classmethod
    def strip_prompt(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Prompt cannot be empty")
        return cleaned

    @field_validator("providers")
    @classmethod
    def normalize_providers(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return None
        unique: list[str] = []
        seen: set[str] = set()
        for item in value:
            key = item.strip().lower()
            if key and key not in seen:
                unique.append(key)
                seen.add(key)
        return unique or None


class ModelInfo(BaseModel):
    id: str
    name: str
    model: str
    family: str
    available: bool
    description: str = ""


class ModelListResponse(BaseModel):
    models: List[ModelInfo]
    available_count: int


class ModelResponse(BaseModel):
    provider_id: str
    provider_name: str
    model: str
    content: str = ""
    latency_ms: int = 0
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    error: Optional[str] = None
    status: str = "ok"


class OrchestrateResponse(BaseModel):
    prompt: str
    mode: str
    responses: List[ModelResponse]
    synthesis: Optional[ModelResponse] = None
    elapsed_ms: int
    providers_used: int
    providers_failed: int
