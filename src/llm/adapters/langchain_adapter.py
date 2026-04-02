from ..domain.enums import AccessMode
from .base import BaseModelAdapter


class LangChainAdapter(BaseModelAdapter):
    access_mode = AccessMode.LANGCHAIN
