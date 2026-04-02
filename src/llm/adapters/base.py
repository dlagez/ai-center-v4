from __future__ import annotations

from abc import ABC
from typing import Any

from ..domain.enums import AccessMode
from ..domain.model_profile import ModelProfile
from ..domain.provider import Provider
from ..domain.request import ChatRequest, EmbeddingRequest, RerankRequest
from ..domain.response import ChatResponse, EmbeddingResponse, RerankResponse
from ..exceptions.errors import AdapterInvocationNotImplementedError


class BaseModelAdapter(ABC):
    access_mode: AccessMode

    def __init__(self, provider: Provider, model: ModelProfile) -> None:
        self.provider = provider
        self.model = model
        self.runtime_config = provider.merged_config(model.meta)

    @classmethod
    def supports(cls, access_mode: AccessMode) -> bool:
        return cls.access_mode == access_mode

    def chat(self, request: ChatRequest) -> ChatResponse:
        raise AdapterInvocationNotImplementedError(
            access_mode=self.model.access_mode.value,
            capability=self.model.capability.value,
            detail=self._build_detail("chat", request),
        )

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        raise AdapterInvocationNotImplementedError(
            access_mode=self.model.access_mode.value,
            capability=self.model.capability.value,
            detail=self._build_detail("embedding", request),
        )

    def rerank(self, request: RerankRequest) -> RerankResponse:
        raise AdapterInvocationNotImplementedError(
            access_mode=self.model.access_mode.value,
            capability=self.model.capability.value,
            detail=self._build_detail("rerank", request),
        )

    def _build_detail(self, operation: str, request: Any) -> dict[str, Any]:
        return {
            "operation": operation,
            "provider_id": self.provider.provider_id,
            "model_id": self.model.model_id,
            "upstream_model_name": self.model.upstream_model_name,
            "request": request.to_dict(),
            "runtime_config": self.runtime_config,
        }
