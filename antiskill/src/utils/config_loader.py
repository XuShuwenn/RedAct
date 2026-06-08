"""Configuration loading utilities."""

import os
import yaml
from pathlib import Path
from typing import Any, Optional

_default_config = None


class ConfigLoader:
    """YAML configuration loader."""

    DEFAULT_CONFIG_PATH = "antiskill/src/configs/default.yaml"

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> dict:
        """
        Load configuration.

        Args:
            config_path: Config file path. Defaults to default.yaml.

        Returns:
            Configuration dictionary.
        """
        global _default_config

        if config_path is None:
            config_path = cls.DEFAULT_CONFIG_PATH

        config_file = Path(config_path)

        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        _default_config = config
        return config

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key. Dot-separated nested keys are supported,
                such as "llm.model".
            default: Default value.

        Returns:
            Configuration value.
        """
        global _default_config

        if _default_config is None:
            cls.load()

        keys = key.split(".")
        value = _default_config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    @classmethod
    def reload(cls) -> dict:
        """Reload configuration."""
        return cls.load()
