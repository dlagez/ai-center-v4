from ..domain.enums import AccessMode
from .base import BaseParserAdapter


class GatewayAdapter(BaseParserAdapter):
    access_mode = AccessMode.GATEWAY
