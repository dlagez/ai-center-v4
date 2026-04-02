from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class BoundingBox:
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(slots=True)
class ParseChunk:
    chunk_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    page_no: int | None = None
    bbox: BoundingBox | None = None
    section_title: str | None = None
    chunk_type: str | None = None
    source_ref: str | None = None


@dataclass(slots=True)
class ParseResult:
    parser_id: str
    provider_id: str
    document_id: str
    chunks: list[ParseChunk]
    raw_result: Any = None
    extra: dict[str, Any] = field(default_factory=dict)
