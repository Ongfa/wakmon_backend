from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.schemas.orchestrate import (
    ModelListResponse,
    OrchestrateRequest,
    OrchestrateResponse,
)
from app.services.orchestrator import Orchestrator

router = APIRouter(prefix="/orchestrate", tags=["orchestration"])


def get_orchestrator() -> Orchestrator:
    return Orchestrator()


def verify_orchestrate_access(
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


@router.get("/models", response_model=ModelListResponse)
def list_models(
    _: None = Depends(verify_orchestrate_access),
    orchestrator: Orchestrator = Depends(get_orchestrator),
):
    models = [provider.info().to_dict() for provider in orchestrator.all_providers()]
    return {
        "models": models,
        "available_count": sum(1 for model in models if model["available"]),
    }


@router.post("", response_model=OrchestrateResponse)
async def orchestrate(
    payload: OrchestrateRequest,
    _: None = Depends(verify_orchestrate_access),
    orchestrator: Orchestrator = Depends(get_orchestrator),
):
    try:
        result = await orchestrator.run(
            payload.prompt,
            provider_ids=payload.providers,
            system_prompt=payload.system_prompt,
            mode=payload.mode,
            synthesize=payload.synthesize,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return result


@router.post("/stream")
async def orchestrate_stream(
    payload: OrchestrateRequest,
    _: None = Depends(verify_orchestrate_access),
    orchestrator: Orchestrator = Depends(get_orchestrator),
):
    async def event_source():
        async for event, data in orchestrator.run_stream(
            payload.prompt,
            provider_ids=payload.providers,
            system_prompt=payload.system_prompt,
            mode=payload.mode,
            synthesize=payload.synthesize,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
        ):
            yield f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
