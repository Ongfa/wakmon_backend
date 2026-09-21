from __future__ import annotations

import asyncio
import json
from typing import Optional

from app.main import app
from app.api.orchestrate import get_orchestrator
from app.providers.base import LLMProvider, LLMResult
from app.services.orchestrator import Orchestrator


class FakeProvider(LLMProvider):
    def __init__(
        self,
        provider_id: str,
        name: str,
        content: str,
        *,
        delay: float = 0,
        fail: bool = False,
        available: bool = True,
        model: str = "fake-1",
    ) -> None:
        self.id = provider_id
        self.name = name
        self.model = model
        self.family = "fake"
        self.description = "test"
        self._content = content
        self._delay = delay
        self._fail = fail
        self._available = available

    @property
    def available(self) -> bool:
        return self._available

    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        temperature: float = 0.4,
        max_tokens: int = 2048,
        timeout: float = 45.0,
    ) -> LLMResult:
        if self._delay:
            await asyncio.sleep(self._delay)
        if self._fail:
            raise RuntimeError(f"{self.name} boom")
        return LLMResult(
            provider_id=self.id,
            provider_name=self.name,
            model=self.model,
            content=f"{self._content} :: {prompt}",
            prompt_tokens=3,
            completion_tokens=5,
        )


async def test_orchestrator_fans_out_and_isolates_failures():
    orchestrator = Orchestrator(
        providers=[
            FakeProvider("alpha", "Alpha", "alpha-ok"),
            FakeProvider("beta", "Beta", "beta-ok", fail=True),
            FakeProvider("gamma", "Gamma", "gamma-ok"),
        ]
    )
    result = await orchestrator.run("Should I hold cash?", synthesize=False)
    statuses = {item["provider_id"]: item["status"] for item in result["responses"]}
    assert statuses == {"alpha": "ok", "beta": "error", "gamma": "ok"}
    assert result["providers_used"] == 2
    assert result["providers_failed"] == 1
    assert result["synthesis"] is None


async def test_orchestrator_synthesizes_successful_answers():
    orchestrator = Orchestrator(
        providers=[
            FakeProvider("alpha", "Alpha", "Buy quality banks"),
            FakeProvider("beta", "Beta", "Wait for a better entry"),
        ]
    )
    result = await orchestrator.run("HDFC vs Kotak", synthesize=True)
    assert result["synthesis"] is not None
    assert result["synthesis"]["status"] == "ok"
    assert "HDFC vs Kotak" in result["synthesis"]["content"]
    assert result["synthesis"]["provider_id"] == "synthesis"


async def test_orchestrator_errors_when_nothing_is_configured():
    orchestrator = Orchestrator(providers=[FakeProvider("x", "X", "nope", available=False)])
    try:
        await orchestrator.run("hello")
        assert False, "expected LookupError"
    except LookupError:
        pass


def test_list_models_with_injected_providers(client):
    orchestrator = Orchestrator(
        providers=[
            FakeProvider("alpha", "Alpha", "ok"),
            FakeProvider("offline", "Offline", "nope", available=False),
        ]
    )
    app.dependency_overrides[get_orchestrator] = lambda: orchestrator
    response = client.get("/api/v1/orchestrate/models")
    assert response.status_code == 200
    body = response.json()
    assert body["available_count"] == 1
    assert {model["id"] for model in body["models"]} == {"alpha", "offline"}


def test_orchestrate_json_endpoint(client):
    orchestrator = Orchestrator(
        providers=[
            FakeProvider("alpha", "Alpha", "hold"),
            FakeProvider("beta", "Beta", "add"),
        ]
    )
    app.dependency_overrides[get_orchestrator] = lambda: orchestrator
    response = client.post(
        "/api/v1/orchestrate",
        json={"prompt": "Is gold a hedge?", "synthesize": True, "mode": "investment"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["providers_used"] == 2
    assert body["synthesis"]["status"] == "ok"
    assert len(body["responses"]) == 2


def test_orchestrate_rejects_blank_prompt(client):
    response = client.post("/api/v1/orchestrate", json={"prompt": "   "})
    assert response.status_code == 422


def test_orchestrate_stream_emits_sse_events(client):
    orchestrator = Orchestrator(
        providers=[
            FakeProvider("alpha", "Alpha", "one"),
            FakeProvider("beta", "Beta", "two"),
        ]
    )
    app.dependency_overrides[get_orchestrator] = lambda: orchestrator
    with client.stream(
        "POST",
        "/api/v1/orchestrate/stream",
        json={"prompt": "Compare two IT majors", "synthesize": True},
    ) as response:
        assert response.status_code == 200
        payload = "".join(response.iter_text())

    events = [line[7:] for line in payload.splitlines() if line.startswith("event: ")]
    assert "council_start" in events
    assert "model_start" in events
    assert "model_complete" in events
    assert "synthesis" in events
    assert "done" in events
    assert "data: " in payload
    # Ensure SSE data is valid JSON
    for line in payload.splitlines():
        if line.startswith("data: "):
            json.loads(line[6:])
