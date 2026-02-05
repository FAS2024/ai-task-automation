from __future__ import annotations

from typing import Protocol

from langchain_openai import ChatOpenAI

from app.core.config import get_settings


class LLM(Protocol):
    def invoke(self, prompt: str) -> str:  # pragma: no cover - protocol only
        ...


class MockLLM:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def invoke(self, prompt: str) -> str:
        trimmed = prompt.strip().replace("\n", " ")
        if len(trimmed) > 120:
            trimmed = f"{trimmed[:117]}..."
        return (
            "MOCK_RESPONSE "
            f"(model={self.model_name}) "
            f"summary='{trimmed}'"
        )


def get_llm() -> LLM:
    settings = get_settings()
    if not settings.openai_api_key:
        return MockLLM(settings.openai_model)

    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        temperature=0.2,
    )
