"""Watermarker module for injecting behavioral watermarks into trajectories."""

from .abstract_watermark import AbstractWatermark
from .registry import WatermarkRegistry, register_watermark
from .trigger_handler import TriggerHandler, WATERMARK_TRIGGERS, detect_trigger, get_trigger_type

# Convenience import for all concrete watermarks
from .task_start_ritual import TaskStartRitualWatermark
from .env_check import EnvCheckWatermark
from .cross_check import CrossCheckWatermark
from .error_anchoring import ErrorAnchoringWatermark

ALL_WATERMARKS = [
    TaskStartRitualWatermark,
    EnvCheckWatermark,
    CrossCheckWatermark,
    ErrorAnchoringWatermark,
]

__all__ = [
    "AbstractWatermark",
    "WatermarkRegistry",
    "register_watermark",
    "TaskStartRitualWatermark",
    "EnvCheckWatermark",
    "CrossCheckWatermark",
    "ErrorAnchoringWatermark",
    "ALL_WATERMARKS",
    "TriggerHandler",
    "WATERMARK_TRIGGERS",
    "detect_trigger",
    "get_trigger_type",
]
