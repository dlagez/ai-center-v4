from __future__ import annotations

from ..adapters.base import BaseParserAdapter
from ..domain.enums import AccessMode
from ..exceptions.errors import AdapterNotFoundError, ConfigurationError


class AdapterRegistry:
    def __init__(self) -> None:
        self._adapters: dict[AccessMode, type[BaseParserAdapter]] = {}

    def register(self, adapter_cls: type[BaseParserAdapter]) -> None:
        access_mode = getattr(adapter_cls, "access_mode", None)
        if access_mode is None:
            raise ConfigurationError(
                f"Adapter '{adapter_cls.__name__}' must define access_mode."
            )
        self._adapters[access_mode] = adapter_cls

    def get(self, access_mode: AccessMode) -> type[BaseParserAdapter]:
        try:
            return self._adapters[access_mode]
        except KeyError as exc:
            raise AdapterNotFoundError(
                f"No adapter registered for access_mode '{access_mode.value}'."
            ) from exc
