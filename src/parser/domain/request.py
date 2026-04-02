from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .enums import SourceType


@dataclass(slots=True)
class InvocationContext:
    tenant_id: str | None = None
    user_id: str | None = None
    request_id: str | None = None
    trace_id: str | None = None
    scene: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ParseRequest:
    parser_id: str
    source_type: SourceType
    source: str | bytes
    file_name: str | None = None
    mime_type: str | None = None
    options: dict[str, Any] = field(default_factory=dict)
    context: InvocationContext | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
