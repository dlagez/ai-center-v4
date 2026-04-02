from __future__ import annotations

from abc import ABC
from typing import Any

from ..domain.enums import AccessMode
from ..domain.parser_profile import ParserProfile
from ..domain.provider import ParserProvider
from ..domain.request import ParseRequest
from ..domain.response import ParseResult
from ..exceptions.errors import AdapterInvocationNotImplementedError


class BaseParserAdapter(ABC):
    access_mode: AccessMode

    def __init__(self, provider: ParserProvider, parser: ParserProfile) -> None:
        self.provider = provider
        self.parser = parser
        self.runtime_config = provider.merged_config(parser.meta)

    @classmethod
    def supports(cls, access_mode: AccessMode) -> bool:
        return cls.access_mode == access_mode

    def parse(self, request: ParseRequest) -> ParseResult:
        raise AdapterInvocationNotImplementedError(
            access_mode=self.parser.access_mode.value,
            capability=self.parser.capability.value,
            detail=self._build_detail(request),
        )

    def _build_detail(self, request: ParseRequest) -> dict[str, Any]:
        return {
            "provider_id": self.provider.provider_id,
            "parser_id": self.parser.parser_id,
            "request": request.to_dict(),
            "runtime_config": self.runtime_config,
        }
