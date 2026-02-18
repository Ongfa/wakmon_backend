from fastapi import APIRouter

from schemas.analysis import InvestmentFormData, AnalysisResult
from services import ai_orchestrator
from core.provider import GeminiProvider
from schemas.test_schema import SimpleAIResponse


router = APIRouter()


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
    text = result["candidates"][0]["content"]["parts"][0]["text"]

    return SimpleAIResponse.model_validate_json(text)


@router.post("/portfolio/analyze", response_model=AnalysisResult)
async def analyze_portfolio(data: InvestmentFormData):
    result = await ai_orchestrator.analyze(data)
    return result
