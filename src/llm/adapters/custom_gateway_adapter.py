from ..domain.enums import AccessMode
from .base import BaseModelAdapter


class CustomGatewayAdapter(BaseModelAdapter):
    access_mode = AccessMode.CUSTOM_GATEWAY
