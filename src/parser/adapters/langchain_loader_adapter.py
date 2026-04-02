from ..domain.enums import AccessMode
from .base import BaseParserAdapter


class LangChainLoaderAdapter(BaseParserAdapter):
    access_mode = AccessMode.LANGCHAIN_LOADER
