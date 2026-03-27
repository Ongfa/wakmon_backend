import httpx
from core.config import GEMINI_API_KEY


class GeminiProvider:

    async def generate(self, prompt: str):
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{url}?key={GEMINI_API_KEY}",
                headers=headers,
                json=payload
            )

        return response.json()
