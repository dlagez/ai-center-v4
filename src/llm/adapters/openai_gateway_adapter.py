from ..domain.enums import AccessMode
from .base import BaseModelAdapter


class OpenAIGatewayAdapter(BaseModelAdapter):
    access_mode = AccessMode.OPENAI_GATEWAY
