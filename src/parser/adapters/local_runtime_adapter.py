from ..domain.enums import AccessMode
from .base import BaseParserAdapter


class LocalRuntimeAdapter(BaseParserAdapter):
    access_mode = AccessMode.LOCAL_RUNTIME
