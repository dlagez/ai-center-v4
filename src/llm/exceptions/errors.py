class LLMError(Exception):
    pass


class ConfigurationError(LLMError):
    pass


class AdapterNotFoundError(LLMError):
    pass


class ProviderNotFoundError(LLMError):
    pass


class ProviderDisabledError(LLMError):
    pass


class ModelNotFoundError(LLMError):
    pass


class ModelDisabledError(LLMError):
    pass


class UnsupportedCapabilityError(LLMError):
    pass


class AdapterInvocationNotImplementedError(LLMError):
    def __init__(self, access_mode: str, capability: str, detail: dict) -> None:
        self.access_mode = access_mode
        self.capability = capability
        self.detail = detail
        super().__init__(
            f"Adapter '{access_mode}' does not implement capability '{capability}' yet."
        )
