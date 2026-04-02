from pathlib import Path

from .adapters.custom_gateway_adapter import CustomGatewayAdapter
from .adapters.langchain_adapter import LangChainAdapter
from .adapters.litellm_adapter import LiteLLMAdapter
from .adapters.local_runtime_adapter import LocalRuntimeAdapter
from .adapters.native_sdk_adapter import NativeSDKAdapter
from .adapters.openai_gateway_adapter import OpenAIGatewayAdapter
from .loaders.config_loader import ConfigLoader
from .registry.adapter_registry import AdapterRegistry
from .registry.model_registry import ModelRegistry
from .registry.provider_registry import ProviderRegistry
from .services.model_service import ModelService


def build_model_service(config_dir: str | Path) -> ModelService:
    loader = ConfigLoader(config_dir)
    providers = loader.load_providers()
    models = loader.load_models()

    provider_registry = ProviderRegistry()
    provider_registry.load(providers)

    model_registry = ModelRegistry(provider_registry)
    model_registry.load(models)

    adapter_registry = AdapterRegistry()
    for adapter_cls in (
        LiteLLMAdapter,
        LangChainAdapter,
        OpenAIGatewayAdapter,
        CustomGatewayAdapter,
        NativeSDKAdapter,
        LocalRuntimeAdapter,
    ):
        adapter_registry.register(adapter_cls)

    return ModelService(
        adapter_registry=adapter_registry,
        provider_registry=provider_registry,
        model_registry=model_registry,
    )
