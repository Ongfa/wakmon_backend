from core.provider import GeminiProvider
from core.validator import validate_with_retry
from schemas.analysis import AnalysisResult


class AIOrchestrator:

    async def analyze(self, data):
        prompt = self._build_prompt(data)

        raw_response = await GeminiProvider().generate(prompt)

        validated = await validate_with_retry(
            raw_response,
            AnalysisResult
        )

        return validated
