from pathlib import Path

from .adapters.custom_service_adapter import CustomServiceAdapter
from .adapters.gateway_adapter import GatewayAdapter
from .adapters.langchain_loader_adapter import LangChainLoaderAdapter
from .adapters.local_runtime_adapter import LocalRuntimeAdapter
from .adapters.native_sdk_adapter import NativeSDKAdapter
from .loaders.config_loader import ConfigLoader
from .registry.adapter_registry import AdapterRegistry
from .registry.parser_registry import ParserRegistry
from .registry.provider_registry import ProviderRegistry
from .services.parse_service import ParseService


def build_parse_service(config_dir: str | Path) -> ParseService:
    loader = ConfigLoader(config_dir)
    providers = loader.load_providers()
    parsers = loader.load_parsers()

    provider_registry = ProviderRegistry()
    provider_registry.load(providers)

    parser_registry = ParserRegistry(provider_registry)
    parser_registry.load(parsers)

    adapter_registry = AdapterRegistry()
    for adapter_cls in (
        NativeSDKAdapter,
        LangChainLoaderAdapter,
        CustomServiceAdapter,
        LocalRuntimeAdapter,
        GatewayAdapter,
    ):
        adapter_registry.register(adapter_cls)

    return ParseService(
        adapter_registry=adapter_registry,
        provider_registry=provider_registry,
        parser_registry=parser_registry,
    )
