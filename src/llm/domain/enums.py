from enum import Enum


class AccessMode(str, Enum):
    LITELLM = "litellm"
    LANGCHAIN = "langchain"
    OPENAI_GATEWAY = "openai_gateway"
    CUSTOM_GATEWAY = "custom_gateway"
    NATIVE_SDK = "native_sdk"
    LOCAL_RUNTIME = "local_runtime"


class Capability(str, Enum):
    CHAT = "chat"
    EMBEDDING = "embedding"
    RERANK = "rerank"
    IMAGE_GENERATION = "image_generation"
    IMAGE_UNDERSTANDING = "image_understanding"
    SPEECH_TO_TEXT = "speech_to_text"
    TEXT_TO_SPEECH = "text_to_speech"
