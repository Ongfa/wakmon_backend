from schemas.analysis import AnalysisResult, InvestmentFormData
from services.ai_orchestrator import AIOrchestrator


class PortfolioService:
    def __init__(self):
        self.orchestrator = AIOrchestrator()

    async def analyze_portfolio(self, data: InvestmentFormData) -> AnalysisResult:
        result = await self.orchestrator.analyze(data)
        return result
