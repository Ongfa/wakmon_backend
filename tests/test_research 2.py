from __future__ import annotations

from typing import Optional

from app.api.deps import get_llm_provider
from app.main import app
from app.providers.base import LLMProvider, LLMResult
from app.services.llm import extract_json


class JsonProvider(LLMProvider):
    def __init__(self, payload: str) -> None:
        self.id = "json"
        self.name = "JSON"
        self.model = "fake"
        self.family = "fake"
        self.description = "test"
        self._payload = payload

    @property
    def available(self) -> bool:
        return True

    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        temperature: float = 0.4,
        max_tokens: int = 2048,
        timeout: float = 45.0,
    ) -> LLMResult:
        return LLMResult(
            provider_id=self.id,
            provider_name=self.name,
            model=self.model,
            content=self._payload,
        )


def test_extract_json_strips_fences():
    assert extract_json('```json\n{"stocks":[1]}\n```') == {"stocks": [1]}


def test_extract_json_finds_embedded_object():
    assert extract_json('Here you go:\n{"ok": true}\n') == {"ok": True}


def test_market_picks_endpoint(client):
    app.dependency_overrides[get_llm_provider] = lambda: JsonProvider(
        '{"stocks":[{"stock_name":"Test","ticker":"TST","sector":"Tech","current_price":10,"change_percentage":1,"description":"x"}]}'
    )
    response = client.get("/api/v1/research/market-picks")
    assert response.status_code == 200
    assert response.json()["stocks"][0]["ticker"] == "TST"


def test_discover_companies_endpoint(client):
    app.dependency_overrides[get_llm_provider] = lambda: JsonProvider(
        '{"companies":[{"stock_name":"Acme","ticker":"ACM"}]}'
    )
    response = client.get("/api/v1/research/discover-companies")
    assert response.status_code == 200
    assert response.json()["companies"][0]["ticker"] == "ACM"


def test_company_details_endpoint(client):
    app.dependency_overrides[get_llm_provider] = lambda: JsonProvider(
        '{"stock_name":"Acme","ticker":"ACM","sector":"Tech"}'
    )
    response = client.post(
        "/api/v1/research/company-details",
        json={"ticker": "acm", "stock_name": "Acme", "sector": "Tech"},
    )
    assert response.status_code == 200
    assert response.json()["company"]["ticker"] == "ACM"


def test_analyze_investment_endpoint(client):
    app.dependency_overrides[get_llm_provider] = lambda: JsonProvider(
        '{"recommendation":"HOLD","confidence":60,"riskScore":40,"verdict":"ok"}'
    )
    response = client.post(
        "/api/v1/research/analyze-investment",
        json={
            "financialData": {
                "targetCompanyName": "HDFC Bank",
                "analysisType": "portfolio",
            }
        },
    )
    assert response.status_code == 200
    assert response.json()["analysis"]["recommendation"] == "HOLD"
