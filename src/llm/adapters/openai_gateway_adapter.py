from ..domain.enums import AccessMode
from .litellm_adapter import LiteLLMAdapter


class OpenAIGatewayAdapter(LiteLLMAdapter):
    access_mode = AccessMode.OPENAI_GATEWAY
