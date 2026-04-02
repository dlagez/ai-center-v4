from __future__ import annotations

import base64
import hashlib
import json
import mimetypes
from pathlib import Path
from urllib import request as urllib_request

from ..domain.enums import AccessMode, SourceType
from ..domain.request import ParseRequest
from ..domain.response import ParseChunk, ParseResult
from ..exceptions.errors import ConfigurationError
from .base import BaseParserAdapter


class CustomServiceAdapter(BaseParserAdapter):
    access_mode = AccessMode.CUSTOM_SERVICE

    def parse(self, request: ParseRequest) -> ParseResult:
        endpoint = self.runtime_config.get("endpoint")
        if not endpoint:
            raise ConfigurationError(
                "custom_service adapter requires 'endpoint' in provider.default_config or parser.meta."
            )
        self._validate_request(request)

        payload = self._build_payload(request)
        raw_result = self._post_json(endpoint, payload)
        chunks = self._map_chunks(raw_result, request)

        document_id = self._build_document_id(request)
        return ParseResult(
            parser_id=self.parser.parser_id,
            provider_id=self.provider.provider_id,
            document_id=document_id,
            chunks=chunks,
            raw_result=raw_result,
            extra={
                "endpoint": endpoint,
                "chunk_count": len(chunks),
            },
        )

    def _build_payload(self, request: ParseRequest) -> dict:
        payload = {
            "file": self._resolve_file_payload(request),
            "fileType": self._resolve_file_type(request),
            "visualize": self.runtime_config.get("visualize", False),
            "use_textline_orientation": self.runtime_config.get(
                "use_textline_orientation", False
            ),
            "use_doc_unwarping": self.runtime_config.get("use_doc_unwarping", False),
            "use_doc_orientation_classify": self.runtime_config.get(
                "use_doc_orientation_classify", False
            ),
        }

        for key, value in request.options.items():
            payload[key] = value
        return payload

    def _validate_request(self, request: ParseRequest) -> None:
        file_name = (request.file_name or "").lower()
        mime_type = (request.mime_type or "").lower()
        is_pdf = file_name.endswith(".pdf") or mime_type == "application/pdf"
        if not is_pdf:
            raise ConfigurationError(
                "ppocr pdf ocr parser only supports PDF input. "
                "Provide a .pdf file_name or mime_type='application/pdf'."
            )

    def _resolve_file_payload(self, request: ParseRequest) -> str:
        if request.source_type == SourceType.FILE_PATH:
            path = Path(str(request.source))
            return base64.b64encode(path.read_bytes()).decode("utf-8")
        if request.source_type == SourceType.BYTES:
            source = request.source
            if not isinstance(source, bytes):
                raise ValueError("ParseRequest.source must be bytes for source_type='bytes'.")
            return base64.b64encode(source).decode("utf-8")
        if request.source_type == SourceType.URL:
            return str(request.source)
        raise ValueError(
            "custom_service adapter supports only 'file_path', 'bytes', and 'url' source types."
        )

    def _resolve_file_type(self, request: ParseRequest) -> int:
        file_name = (request.file_name or "").lower()
        mime_type = (request.mime_type or "").lower()

        if file_name.endswith(".pdf") or mime_type == "application/pdf":
            return 0

        guessed_mime, _ = mimetypes.guess_type(request.file_name or "")
        if guessed_mime == "application/pdf":
            return 0
        return 1

    def _post_json(self, endpoint: str, payload: dict) -> dict:
        timeout = float(self.runtime_config.get("timeout_seconds", 60))
        headers = {
            "Content-Type": "application/json",
            **self.runtime_config.get("headers", {}),
        }
        body = json.dumps(payload).encode("utf-8")
        request_obj = urllib_request.Request(
            endpoint,
            data=body,
            headers=headers,
            method="POST",
        )
        with urllib_request.urlopen(request_obj, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def _map_chunks(self, raw_result: dict, request: ParseRequest) -> list[ParseChunk]:
        ocr_results = (
            raw_result.get("result", {}).get("ocrResults", [])
            if isinstance(raw_result, dict)
            else []
        )

        chunks: list[ParseChunk] = []
        document_id = self._build_document_id(request)
        for index, entry in enumerate(ocr_results):
            texts = entry.get("prunedResult", {}).get("rec_texts", [])
            text = " ".join(str(item).strip() for item in texts if str(item).strip())
            if not text:
                continue

            chunks.append(
                ParseChunk(
                    chunk_id=f"{document_id}:{index}",
                    text=text,
                    metadata={
                        "parser": self.parser.parser_id,
                        "provider": self.provider.provider_id,
                        "chunk_index": index,
                        "source_type": request.source_type.value,
                        "file_name": request.file_name,
                        "mime_type": request.mime_type,
                    },
                    chunk_type="text",
                    source_ref=request.file_name or str(request.source),
                )
            )

        if chunks:
            return chunks

        fallback_text = raw_result.get("result", {}).get("text", "") if isinstance(raw_result, dict) else ""
        if fallback_text:
            return [
                ParseChunk(
                    chunk_id=f"{document_id}:0",
                    text=str(fallback_text),
                    metadata={
                        "parser": self.parser.parser_id,
                        "provider": self.provider.provider_id,
                        "source_type": request.source_type.value,
                        "file_name": request.file_name,
                        "mime_type": request.mime_type,
                    },
                    chunk_type="text",
                    source_ref=request.file_name or str(request.source),
                )
            ]
        return []

    def _build_document_id(self, request: ParseRequest) -> str:
        raw_source = request.source
        if isinstance(raw_source, bytes):
            source_value = hashlib.sha256(raw_source).hexdigest()
        else:
            source_value = str(raw_source)
        basis = f"{self.parser.parser_id}|{request.file_name}|{source_value}"
        return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:24]
