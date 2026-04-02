from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Usage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(slots=True)
class ChatResponse:
    model_id: str
    provider_id: str
    content: str
    raw_response: Any = None
    usage: Usage | None = None
    finish_reason: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EmbeddingResponse:
    model_id: str
    provider_id: str
    vectors: list[list[float]]
    usage: Usage | None = None
    raw_response: Any = None


@dataclass(slots=True)
class RerankResult:
    index: int
    score: float
    document: str


@dataclass(slots=True)
class RerankResponse:
    model_id: str
    provider_id: str
    results: list[RerankResult]
    raw_response: Any = None
