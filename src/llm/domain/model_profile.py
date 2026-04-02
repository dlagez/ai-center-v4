from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .enums import AccessMode, Capability


@dataclass(slots=True)
class ModelProfile:
    model_id: str
    model_name: str
    provider_id: str
    access_mode: AccessMode
    capability: Capability
    upstream_model_name: str
    enabled: bool = True
    is_default: bool = False
    timeout: int | None = None
    max_retries: int | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelProfile":
        return cls(
            model_id=data["model_id"],
            model_name=data["model_name"],
            provider_id=data["provider_id"],
            access_mode=AccessMode(data["access_mode"]),
            capability=Capability(data["capability"]),
            upstream_model_name=data["upstream_model_name"],
            enabled=data.get("enabled", True),
            is_default=data.get("is_default", False),
            timeout=data.get("timeout"),
            max_retries=data.get("max_retries"),
            meta=dict(data.get("meta", {})),
        )
