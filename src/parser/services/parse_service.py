from __future__ import annotations

from ..domain.enums import ParseCapability
from ..domain.parser_profile import ParserProfile
from ..domain.request import ParseRequest
from ..domain.response import ParseResult
from ..exceptions.errors import UnsupportedCapabilityError
from ..registry.adapter_registry import AdapterRegistry
from ..registry.parser_registry import ParserRegistry
from ..registry.provider_registry import ProviderRegistry


class ParseService:
    def __init__(
        self,
        *,
        adapter_registry: AdapterRegistry,
        provider_registry: ProviderRegistry,
        parser_registry: ParserRegistry,
    ) -> None:
        self.adapter_registry = adapter_registry
        self.provider_registry = provider_registry
        self.parser_registry = parser_registry

    def parse(self, request: ParseRequest) -> ParseResult:
        parser, provider, adapter = self._resolve(
            request.parser_id, ParseCapability.DOCUMENT_PARSE
        )
        return adapter(provider, parser).parse(request)

    def get_default_parser(self, capability: ParseCapability) -> ParserProfile:
        return self.parser_registry.get_default(capability)

    def _resolve(self, parser_id: str, capability: ParseCapability):
        parser = self.parser_registry.get(parser_id)
        if parser.capability != capability:
            raise UnsupportedCapabilityError(
                f"Parser '{parser_id}' capability is '{parser.capability.value}', "
                f"expected '{capability.value}'."
            )

        provider = self.provider_registry.get(parser.provider_id)
        adapter_cls = self.adapter_registry.get(parser.access_mode)
        return parser, provider, adapter_cls
