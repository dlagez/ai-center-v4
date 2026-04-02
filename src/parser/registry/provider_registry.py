from __future__ import annotations

from ..domain.provider import ParserProvider
from ..exceptions.errors import ConfigurationError, ProviderDisabledError, ProviderNotFoundError


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, ParserProvider] = {}

    def load(self, providers: list[ParserProvider]) -> None:
        self._providers.clear()
        for provider in providers:
            if provider.provider_id in self._providers:
                raise ConfigurationError(
                    f"Duplicate provider_id '{provider.provider_id}'."
                )
            self._providers[provider.provider_id] = provider

    def get(self, provider_id: str, *, require_enabled: bool = True) -> ParserProvider:
        try:
            provider = self._providers[provider_id]
        except KeyError as exc:
            raise ProviderNotFoundError(
                f"Provider '{provider_id}' does not exist."
            ) from exc

        if require_enabled and not provider.enabled:
            raise ProviderDisabledError(f"Provider '{provider_id}' is disabled.")
        return provider
