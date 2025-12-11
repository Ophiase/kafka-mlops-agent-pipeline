from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, Optional


class ServicePhase(Enum):
    """High-level lifecycle stages for long-running services."""

    STOPPED = auto()
    STARTING = auto()
    RUNNING = auto()
    STOPPING = auto()
    ERROR = auto()


@dataclass
class ServiceState:
    """Represents the current status of a controllable service."""

    phase: ServicePhase = ServicePhase.STOPPED
    iterations: int = 0
    last_error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase.name.lower(),
            "iterations": self.iterations,
            "last_error": self.last_error,
            "metadata": self.metadata,
            "updated_at": self.updated_at.isoformat(),
        }

    def mark(
        self,
        phase: ServicePhase,
        *,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update the state with the provided lifecycle info."""

        self.phase = phase
        self.last_error = error
        if metadata:
            self.metadata.update(metadata)
        self.updated_at = datetime.utcnow()

    def increment_iterations(
        self, *, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        self.iterations += 1
        if metadata:
            self.metadata.update(metadata)
        self.updated_at = datetime.utcnow()
