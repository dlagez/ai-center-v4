from ..domain.enums import AccessMode
from .base import BaseParserAdapter


class CustomServiceAdapter(BaseParserAdapter):
    access_mode = AccessMode.CUSTOM_SERVICE
