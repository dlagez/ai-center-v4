from __future__ import annotations

import os
from typing import Any

import litellm

from ..domain.enums import AccessMode
from ..domain.request import ChatRequest, EmbeddingRequest
from ..domain.response import ChatResponse, EmbeddingResponse, Usage
from ..exceptions.errors import ConfigurationError, UnsupportedCapabilityError
from .base import BaseModelAdapter


class LiteLLMAdapter(BaseModelAdapter):
    access_mode = AccessMode.LITELLM

    def chat(self, request: ChatRequest) -> ChatResponse:
        if request.stream:
            raise UnsupportedCapabilityError(
                "Streaming chat is not supported by the current ChatResponse contract."
            )

        response = litellm.completion(
            model=self._resolved_model_name(),
            messages=[self._message_to_dict(message) for message in request.messages],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            tools=request.tools or None,
            response_format=request.response_format,
            stream=False,
            **self._client_kwargs(),
        )
        payload = self._to_dict(response)
        choice = (payload.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        return ChatResponse(
            model_id=self.model.model_id,
            provider_id=self.provider.provider_id,
            content=self._normalize_content(message.get("content")),
            raw_response=payload,
            usage=self._parse_usage(payload.get("usage")),
            finish_reason=choice.get("finish_reason"),
            extra={"upstream_model_name": payload.get("model", self.model.upstream_model_name)},
        )

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        response = litellm.embedding(
            model=self._resolved_model_name(),
            input=request.texts,
            **self._client_kwargs(),
        )
        payload = self._to_dict(response)
        vectors = [
            item.get("embedding", [])
            for item in sorted(payload.get("data", []), key=lambda item: item.get("index", 0))
        ]
        return EmbeddingResponse(
            model_id=self.model.model_id,
            provider_id=self.provider.provider_id,
            vectors=vectors,
            usage=self._parse_usage(payload.get("usage")),
            raw_response=payload,
        )

    def _client_kwargs(self) -> dict[str, Any]:
        config = dict(self.runtime_config)
        extra = dict(config.pop("litellm_params", {}))

        api_key = config.pop("api_key", None)
        api_key_env = config.pop("api_key_env", None)
        if api_key is None and api_key_env:
            api_key = os.getenv(api_key_env)
            if not api_key:
                raise ConfigurationError(
                    f"Environment variable '{api_key_env}' is not set for provider "
                    f"'{self.provider.provider_id}'."
                )

        api_base = config.pop("api_base", None) or config.pop("base_url", None)
        timeout = config.pop("timeout", None) or self.model.timeout
        num_retries = config.pop("num_retries", None) or self.model.max_retries

        custom_llm_provider = config.pop("custom_llm_provider", None)
        if custom_llm_provider is None and api_base:
            custom_llm_provider = "openai"

        kwargs = {
            "api_key": api_key,
            "api_base": api_base,
            "organization": config.pop("organization", None),
            "api_version": config.pop("api_version", None),
            "custom_llm_provider": custom_llm_provider,
            "extra_headers": config.pop("extra_headers", None)
            or config.pop("default_headers", None),
            "timeout": timeout,
            "num_retries": num_retries,
            "drop_params": config.pop("drop_params", True),
        }
        kwargs.update(extra)
        return {key: value for key, value in kwargs.items() if value is not None}

    def _message_to_dict(self, message: Any) -> dict[str, Any]:
        if hasattr(message, "role") and hasattr(message, "content"):
            return {"role": message.role, "content": message.content}
        if isinstance(message, dict):
            return message
        raise ConfigurationError(f"Unsupported chat message type: {type(message)!r}")

    def _parse_usage(self, usage: Any) -> Usage | None:
        if usage is None:
            return None
        payload = self._to_dict(usage)
        return Usage(
            prompt_tokens=payload.get("prompt_tokens"),
            completion_tokens=payload.get("completion_tokens"),
            total_tokens=payload.get("total_tokens"),
        )

    def _resolved_model_name(self) -> str:
        if "/" in self.model.upstream_model_name:
            return self.model.upstream_model_name

        config = self.runtime_config
        custom_llm_provider = config.get("custom_llm_provider")
        base_url = config.get("api_base") or config.get("base_url")
        if custom_llm_provider == "openai" or base_url:
            return f"openai/{self.model.upstream_model_name}"
        return self.model.upstream_model_name

    def _normalize_content(self, content: Any) -> str:
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                    continue
                if isinstance(item, dict) and item.get("type") == "text":
                    text = item.get("text")
                    if text:
                        parts.append(str(text))
            return "".join(parts)
        return str(content)

    def _to_dict(self, value: Any) -> dict[str, Any]:
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        if hasattr(value, "model_dump"):
            return value.model_dump()
        if hasattr(value, "dict"):
            return value.dict()
        raise ConfigurationError(f"Unsupported LiteLLM response type: {type(value)!r}")
