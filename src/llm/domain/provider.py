from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .enums import AccessMode


@dataclass(slots=True)
class Provider:
    provider_id: str
    provider_type: str
    name: str
    access_mode: AccessMode
    enabled: bool = True
    default_config: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Provider":
        return cls(
            provider_id=data["provider_id"],
            provider_type=data["provider_type"],
            name=data["name"],
            access_mode=AccessMode(data["access_mode"]),
            enabled=data.get("enabled", True),
            default_config=dict(data.get("default_config", {})),
        )

    def merged_config(self, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
        merged = dict(self.default_config)
        if overrides:
            merged.update(overrides)
        return merged
