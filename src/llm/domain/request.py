from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class InvocationContext:
    tenant_id: str | None = None
    user_id: str | None = None
    request_id: str | None = None
    scene: str | None = None
    trace_id: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ChatMessage:
    role: str
    content: str


@dataclass(slots=True)
class ChatRequest:
    model_id: str
    messages: list[ChatMessage]
    temperature: float | None = None
    max_tokens: int | None = None
    stream: bool = False
    tools: list[dict[str, Any]] = field(default_factory=list)
    response_format: dict[str, Any] | None = None
    context: InvocationContext | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class EmbeddingRequest:
    model_id: str
    texts: list[str]
    context: InvocationContext | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RerankRequest:
    model_id: str
    query: str
    documents: list[str]
    top_k: int | None = None
    context: InvocationContext | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
