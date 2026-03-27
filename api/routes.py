from fastapi import APIRouter

from schemas.analysis import InvestmentFormData, AnalysisResult
from services.portfolio_service import PortfolioService
from core.provider import GeminiProvider
from schemas.test_schema import SimpleAIResponse
from schemas.financial import FinancialInput, RedFlagResult
from services.financial_engine import compute_metrics, detect_mechanical_flags

router = APIRouter()
portfolio_service = PortfolioService()


@router.get("/")
async def read_root():
    return {"Hello": "World"}


@router.post("/test", response_model=SimpleAIResponse)
async def test_ai():
    provider = GeminiProvider()
    result = await provider.generate(
        "Return JSON like this: {\"message\": \"hello\"}. Only JSON."
    )

    # Extract text from Gemini response
    print("FULL RESULT:", result)

    return result
    # text = result["choices"][0]["content"]["parts"][0]["text"]
    #
    # return SimpleAIResponse.model_validate_json(text)


@router.post("/portfolio/analyze", response_model=AnalysisResult)
async def analyze_portfolio(data: InvestmentFormData):
    result = await portfolio_service.analyze_portfolio(data)
    return result


@router.post("/financial/redflags", response_model=RedFlagResult)
async def financial_redflags(data: FinancialInput):
    metrics = compute_metrics(data)
    flags = detect_mechanical_flags(metrics)

    return RedFlagResult(
        metrics=metrics,
        red_flags=flags
    )
