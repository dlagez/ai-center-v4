class ParserError(Exception):
    pass


class ConfigurationError(ParserError):
    pass


class AdapterNotFoundError(ParserError):
    pass


class ProviderNotFoundError(ParserError):
    pass


class ProviderDisabledError(ParserError):
    pass


class ParserNotFoundError(ParserError):
    pass


class ParserDisabledError(ParserError):
    pass


class UnsupportedCapabilityError(ParserError):
    pass


class AdapterInvocationNotImplementedError(ParserError):
    def __init__(self, access_mode: str, capability: str, detail: dict) -> None:
        self.access_mode = access_mode
        self.capability = capability
        self.detail = detail
        super().__init__(
            f"Adapter '{access_mode}' does not implement capability '{capability}' yet."
        )
