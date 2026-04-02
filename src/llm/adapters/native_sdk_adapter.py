from ..domain.enums import AccessMode
from .base import BaseModelAdapter


class NativeSDKAdapter(BaseModelAdapter):
    access_mode = AccessMode.NATIVE_SDK
