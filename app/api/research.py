from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_llm_provider, verify_llm_access
from app.providers.base import LLMProvider
from app.schemas.research import (
    AnalyzeInvestmentRequest,
    AnalyzeInvestmentResponse,
    CompanyDetailsRequest,
    CompanyDetailsResponse,
    DiscoverCompaniesResponse,
    MarketPicksResponse,
)
from app.services import research as research_service

router = APIRouter(prefix="/research", tags=["research"])


def _http_error(exc: Exception) -> HTTPException:
    return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))


@router.get("/market-picks", response_model=MarketPicksResponse)
@router.post("/market-picks", response_model=MarketPicksResponse)
async def market_picks(
    _: None = Depends(verify_llm_access),
    provider: LLMProvider = Depends(get_llm_provider),
):
    try:
        return await research_service.fetch_market_picks(provider)
    except Exception as exc:
        raise _http_error(exc) from exc


@router.get("/discover-companies", response_model=DiscoverCompaniesResponse)
@router.post("/discover-companies", response_model=DiscoverCompaniesResponse)
async def discover_companies(
    _: None = Depends(verify_llm_access),
    provider: LLMProvider = Depends(get_llm_provider),
):
    try:
        return await research_service.fetch_discover_companies(provider)
    except Exception as exc:
        raise _http_error(exc) from exc


@router.post("/company-details", response_model=CompanyDetailsResponse)
async def company_details(
    payload: CompanyDetailsRequest,
    _: None = Depends(verify_llm_access),
    provider: LLMProvider = Depends(get_llm_provider),
):
    try:
        return await research_service.fetch_company_details(provider, payload)
    except Exception as exc:
        raise _http_error(exc) from exc


@router.post("/analyze-investment", response_model=AnalyzeInvestmentResponse)
async def analyze_investment(
    payload: AnalyzeInvestmentRequest,
    _: None = Depends(verify_llm_access),
    provider: LLMProvider = Depends(get_llm_provider),
):
    try:
        return await research_service.analyze_investment(provider, payload.financialData)
    except Exception as exc:
        raise _http_error(exc) from exc
