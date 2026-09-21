from __future__ import annotations

from typing import Optional

from fastapi import Header, HTTPException, status

from app.core.config import settings
from app.providers.base import LLMProvider
from app.services.llm import pick_provider


def verify_llm_access(
    x_orchestrate_key: Optional[str] = Header(default=None, alias="X-Orchestrate-Key"),
) -> None:
    expected = (settings.ORCHESTRATE_API_KEY or "").strip()
    if not expected:
        return
    if (x_orchestrate_key or "").strip() != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid orchestration API key",
        )


def get_llm_provider() -> LLMProvider:
    try:
        return pick_provider()
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
