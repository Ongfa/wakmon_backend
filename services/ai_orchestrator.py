from core.provider import GeminiProvider
from core.validator import validate_with_retry
from schemas.analysis import AnalysisResult, InvestmentFormData


class AIOrchestrator:

    def __init__(self):
        self.provider = GeminiProvider()

    async def analyze(self, data: InvestmentFormData) -> AnalysisResult:
        system_prompt = """
        You are a financial analysis assistant.
        Return ONLY valid JSON matching the required schema.
        """
        user_prompt = f"""
              Analyze the following portfolio data:
              {data.model_dump_json()}
              """
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        validated = await validate_with_retry(
            provider=self.provider,
            prompt=full_prompt,
            schema=AnalysisResult,
            max_retries=2
        )

        return validated
