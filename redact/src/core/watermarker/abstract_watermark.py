"""Abstract base class for watermarks."""

from abc import ABC, abstractmethod
from typing import Any


class AbstractWatermark(ABC):
    """Abstract base class for behavioral watermarks.

    Subclasses must implement:
    - check(): whether watermark can be applied to given trajectory
    - inject(): inject watermark into trajectory and return new trajectory
    - name(): unique identifier for this watermark method
    - description(): human-readable description
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this watermark, e.g. 'ritual_marker'."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this watermark does."""
        pass

    @abstractmethod
    def check(self, trajectory: dict, task_name: str = None) -> bool:
        """Check if watermark can be applied to given trajectory.

        Args:
            trajectory: trajectory dict with 'turns' key
            task_name:  name of the task (from trajectory filename stem), optional

        Returns:
            True if watermark can be applied, False otherwise
        """
        pass

    @abstractmethod
    def inject(self, trajectory: dict, task_name: str = None) -> dict:
        """Inject watermark into trajectory.

        Args:
            trajectory: trajectory dict with 'turns' key
            task_name:  name of the task (from trajectory filename stem), optional

        Returns:
            New trajectory dict with watermark injected (original unchanged)
        """
        pass
