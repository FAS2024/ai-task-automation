from __future__ import annotations

from typing import Any, Protocol

from langchain_core.messages import AIMessage, HumanMessage
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


def _aimessage_content_to_str(content: str | list[str | dict[str, Any]]) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict) and "text" in block:
                parts.append(str(block["text"]))
            else:
                parts.append(str(block))
        return "".join(parts)
    return str(content)


class OpenAIChatLLM:
    """Wraps LangChain 1.x ChatOpenAI so callers can pass a plain string prompt."""

    def __init__(self, chat: ChatOpenAI) -> None:
        self._chat = chat

    def invoke(self, prompt: str) -> str:
        result = self._chat.invoke([HumanMessage(content=prompt)])
        if isinstance(result, AIMessage):
            return _aimessage_content_to_str(result.content)
        return str(result)


def get_llm() -> LLM:
    settings = get_settings()
    if not settings.openai_api_key:
        return MockLLM(settings.openai_model)

    return OpenAIChatLLM(
        ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=0.2,
        )
    )
