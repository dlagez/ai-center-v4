from __future__ import annotations

from ..domain.enums import Capability
from ..domain.model_profile import ModelProfile
from ..exceptions.errors import ConfigurationError, ModelDisabledError, ModelNotFoundError
from .provider_registry import ProviderRegistry


class ModelRegistry:
    def __init__(self, provider_registry: ProviderRegistry) -> None:
        self._provider_registry = provider_registry
        self._models: dict[str, ModelProfile] = {}

    def load(self, models: list[ModelProfile]) -> None:
        self._models.clear()
        defaults: set[Capability] = set()
        for model in models:
            if model.model_id in self._models:
                raise ConfigurationError(f"Duplicate model_id '{model.model_id}'.")

            provider = self._provider_registry.get(model.provider_id, require_enabled=False)
            if provider.access_mode != model.access_mode:
                raise ConfigurationError(
                    f"Model '{model.model_id}' access_mode '{model.access_mode.value}' "
                    f"does not match provider '{provider.provider_id}' access_mode "
                    f"'{provider.access_mode.value}'."
                )

            if model.is_default:
                if model.capability in defaults:
                    raise ConfigurationError(
                        f"Multiple default models configured for capability '{model.capability.value}'."
                    )
                defaults.add(model.capability)

            self._models[model.model_id] = model

    def get(self, model_id: str, *, require_enabled: bool = True) -> ModelProfile:
        try:
            model = self._models[model_id]
        except KeyError as exc:
            raise ModelNotFoundError(f"Model '{model_id}' does not exist.") from exc

        if require_enabled and not model.enabled:
            raise ModelDisabledError(f"Model '{model_id}' is disabled.")
        return model

    def get_default(self, capability: Capability) -> ModelProfile:
        for model in self._models.values():
            if model.capability == capability and model.is_default and model.enabled:
                return model
        raise ModelNotFoundError(
            f"No default model configured for capability '{capability.value}'."
        )

    def list_by_capability(
        self, capability: Capability, *, enabled_only: bool = True
    ) -> list[ModelProfile]:
        return [
            model
            for model in self._models.values()
            if model.capability == capability and (model.enabled or not enabled_only)
        ]
