from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .enums import AccessMode, ParseCapability


@dataclass(slots=True)
class ParserProfile:
    parser_id: str
    parser_name: str
    provider_id: str
    access_mode: AccessMode
    capability: ParseCapability
    enabled: bool = True
    is_default: bool = False
    timeout: int | None = None
    max_retries: int | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ParserProfile":
        return cls(
            parser_id=data["parser_id"],
            parser_name=data["parser_name"],
            provider_id=data["provider_id"],
            access_mode=AccessMode(data["access_mode"]),
            capability=ParseCapability(data["capability"]),
            enabled=data.get("enabled", True),
            is_default=data.get("is_default", False),
            timeout=data.get("timeout"),
            max_retries=data.get("max_retries"),
            meta=dict(data.get("meta", {})),
        )
