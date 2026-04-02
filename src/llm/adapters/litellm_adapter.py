from ..domain.enums import AccessMode
from .base import BaseModelAdapter


class LiteLLMAdapter(BaseModelAdapter):
    access_mode = AccessMode.LITELLM
