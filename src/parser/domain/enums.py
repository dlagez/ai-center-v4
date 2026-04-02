from enum import Enum


class AccessMode(str, Enum):
    NATIVE_SDK = "native_sdk"
    LANGCHAIN_LOADER = "langchain_loader"
    CUSTOM_SERVICE = "custom_service"
    LOCAL_RUNTIME = "local_runtime"
    GATEWAY = "gateway"


class ParseCapability(str, Enum):
    DOCUMENT_PARSE = "document_parse"
    OCR_PARSE = "ocr_parse"
    TABLE_PARSE = "table_parse"
    IMAGE_PARSE = "image_parse"


class SourceType(str, Enum):
    FILE_PATH = "file_path"
    BYTES = "bytes"
    URL = "url"
    TEXT = "text"
