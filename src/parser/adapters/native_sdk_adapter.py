from ..domain.enums import AccessMode
from .base import BaseParserAdapter


class NativeSDKAdapter(BaseParserAdapter):
    access_mode = AccessMode.NATIVE_SDK
