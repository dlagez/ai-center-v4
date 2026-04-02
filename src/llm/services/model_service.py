from __future__ import annotations

from ..domain.enums import Capability
from ..domain.model_profile import ModelProfile
from ..domain.provider import Provider
from ..domain.request import ChatRequest, EmbeddingRequest, RerankRequest
from ..domain.response import ChatResponse, EmbeddingResponse, RerankResponse
from ..exceptions.errors import UnsupportedCapabilityError
from ..registry.adapter_registry import AdapterRegistry
from ..registry.model_registry import ModelRegistry
from ..registry.provider_registry import ProviderRegistry


class ModelService:
    def __init__(
        self,
        *,
        adapter_registry: AdapterRegistry,
        provider_registry: ProviderRegistry,
        model_registry: ModelRegistry,
    ) -> None:
        self.adapter_registry = adapter_registry
        self.provider_registry = provider_registry
        self.model_registry = model_registry

    def chat(self, request: ChatRequest) -> ChatResponse:
        model, provider, adapter = self._resolve(request.model_id, Capability.CHAT)
        return adapter(provider, model).chat(request)

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        model, provider, adapter = self._resolve(request.model_id, Capability.EMBEDDING)
        return adapter(provider, model).embed(request)

    def rerank(self, request: RerankRequest) -> RerankResponse:
        model, provider, adapter = self._resolve(request.model_id, Capability.RERANK)
        return adapter(provider, model).rerank(request)

    def get_default_model(self, capability: Capability) -> ModelProfile:
        return self.model_registry.get_default(capability)

    def _resolve(self, model_id: str, capability: Capability):
        model = self.model_registry.get(model_id)
        if model.capability != capability:
            raise UnsupportedCapabilityError(
                f"Model '{model_id}' capability is '{model.capability.value}', "
                f"expected '{capability.value}'."
            )

        provider = self.provider_registry.get(model.provider_id)
        adapter_cls = self.adapter_registry.get(model.access_mode)
        return model, provider, adapter_cls
