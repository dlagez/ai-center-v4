from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..domain.parser_profile import ParserProfile
from ..domain.provider import ParserProvider
from ..exceptions.errors import ConfigurationError

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


class ConfigLoader:
    def __init__(self, config_dir: str | Path) -> None:
        self.config_dir = Path(config_dir)

    def load_providers(self) -> list[ParserProvider]:
        data = self._load_mapping("providers")
        return [ParserProvider.from_dict(item) for item in data.get("providers", [])]

    def load_parsers(self) -> list[ParserProfile]:
        data = self._load_mapping("parsers")
        return [ParserProfile.from_dict(item) for item in data.get("parsers", [])]

    def _load_mapping(self, name: str) -> dict[str, Any]:
        for extension in ("yaml", "yml", "json"):
            path = self.config_dir / f"{name}.{extension}"
            if path.exists():
                return self._read_file(path)
        raise ConfigurationError(f"Missing config file for '{name}' in {self.config_dir}")

    def _read_file(self, path: Path) -> dict[str, Any]:
        if path.suffix in {".yaml", ".yml"}:
            if yaml is None:
                raise ConfigurationError("PyYAML is required to load YAML config files.")
            with path.open("r", encoding="utf-8") as file:
                return yaml.safe_load(file) or {}

        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
