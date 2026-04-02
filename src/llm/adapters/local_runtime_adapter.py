from ..domain.enums import AccessMode
from .base import BaseModelAdapter


class LocalRuntimeAdapter(BaseModelAdapter):
    access_mode = AccessMode.LOCAL_RUNTIME
