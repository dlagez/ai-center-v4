from __future__ import annotations

from ..domain.enums import ParseCapability
from ..domain.parser_profile import ParserProfile
from ..exceptions.errors import ConfigurationError, ParserDisabledError, ParserNotFoundError
from .provider_registry import ProviderRegistry


class ParserRegistry:
    def __init__(self, provider_registry: ProviderRegistry) -> None:
        self._provider_registry = provider_registry
        self._parsers: dict[str, ParserProfile] = {}

    def load(self, parsers: list[ParserProfile]) -> None:
        self._parsers.clear()
        defaults: set[ParseCapability] = set()
        for parser in parsers:
            if parser.parser_id in self._parsers:
                raise ConfigurationError(f"Duplicate parser_id '{parser.parser_id}'.")

            provider = self._provider_registry.get(parser.provider_id, require_enabled=False)
            if provider.access_mode != parser.access_mode:
                raise ConfigurationError(
                    f"Parser '{parser.parser_id}' access_mode '{parser.access_mode.value}' "
                    f"does not match provider '{provider.provider_id}' access_mode "
                    f"'{provider.access_mode.value}'."
                )

            if parser.is_default:
                if parser.capability in defaults:
                    raise ConfigurationError(
                        "Multiple default parsers configured for capability "
                        f"'{parser.capability.value}'."
                    )
                defaults.add(parser.capability)

            self._parsers[parser.parser_id] = parser

    def get(self, parser_id: str, *, require_enabled: bool = True) -> ParserProfile:
        try:
            parser = self._parsers[parser_id]
        except KeyError as exc:
            raise ParserNotFoundError(f"Parser '{parser_id}' does not exist.") from exc

        if require_enabled and not parser.enabled:
            raise ParserDisabledError(f"Parser '{parser_id}' is disabled.")
        return parser

    def get_default(self, capability: ParseCapability) -> ParserProfile:
        for parser in self._parsers.values():
            if parser.capability == capability and parser.is_default and parser.enabled:
                return parser
        raise ParserNotFoundError(
            f"No default parser configured for capability '{capability.value}'."
        )
