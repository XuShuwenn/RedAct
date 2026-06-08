"""Watermark registry for discovering and instantiating watermarks."""

import logging
from typing import Type

from .abstract_watermark import AbstractWatermark

logger = logging.getLogger(__name__)

_WATERMARK_REGISTRY: dict[str, Type[AbstractWatermark]] = {}


def register_watermark(cls: Type[AbstractWatermark]) -> Type[AbstractWatermark]:
    """Decorator to register a watermark class."""
    name = cls().name
    if name in _WATERMARK_REGISTRY:
        logger.warning(f"Watermark '{name}' already registered, overwriting.")
    _WATERMARK_REGISTRY[name] = cls
    return cls


class WatermarkRegistry:
    """Registry for watermark methods."""

    @classmethod
    def get(cls, name: str) -> Type[AbstractWatermark]:
        """Get watermark class by name."""
        if name not in _WATERMARK_REGISTRY:
            raise KeyError(f"Unknown watermark: '{name}'. Available: {list(_WATERMARK_REGISTRY.keys())}")
        return _WATERMARK_REGISTRY[name]

    @classmethod
    def list_names(cls) -> list[str]:
        """List all registered watermark names."""
        return list(_WATERMARK_REGISTRY.keys())

    @classmethod
    def create(cls, name: str, **kwargs) -> AbstractWatermark:
        """Instantiate a watermark by name."""
        return cls.get(name)(**kwargs)
