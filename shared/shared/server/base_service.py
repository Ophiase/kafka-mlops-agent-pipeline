from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from .service_state import ServicePhase, ServiceState


class BaseService(ABC):
    """Reusable lifecycle helpers for controllable services."""

    def __init__(self, *, loop_delay: float = 0.0, error_backoff: float = 5.0):
        self._loop_delay = max(0.0, loop_delay)
        self._error_backoff = max(0.0, error_backoff)
        self._state = ServiceState()
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start the background loop if it is not already running."""

        with self._lock:
            if self.is_running:
                return
            self._stop_event.clear()
            self._state.mark(ServicePhase.STARTING)
            self._log("Starting background loop")
            self._thread = threading.Thread(
                target=self._loop_entrypoint,
                name=f"{self.__class__.__name__}Loop",
                daemon=True,
            )
            self._thread.start()

    def stop(self, *, wait: bool = True) -> None:
        """Signal the background loop to stop and optionally wait for it."""

        with self._lock:
            thread = self._thread
            if not thread:
                self._state.mark(ServicePhase.STOPPED)
                self._log("Stop requested but loop is not running")
                return
            self._state.mark(ServicePhase.STOPPING)
            self._log(
                "Stop signal sent; waiting for loop to exit"
                if wait
                else "Stop signal sent"
            )
            self._stop_event.set()

        if wait:
            thread.join()
            self._log("Loop joined")

        with self._lock:
            self._thread = None

    def wait(self, timeout: Optional[float] = None) -> None:
        """Block until the background thread finishes, if running."""

        thread = self._thread
        if thread and thread.is_alive():
            thread.join(timeout=timeout)

    def run_iteration(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute a single iteration synchronously."""

        return self._execute_iteration(**kwargs)

    def configure(self, **kwargs: Any) -> None:
        """Optional hook subclasses may override to tweak runtime options."""

        raise NotImplementedError("configure() is not implemented for this service")

    def status(self) -> ServiceState:
        return self._state

    @property
    def is_running(self) -> bool:
        thread = self._thread
        return bool(thread and thread.is_alive())

    def _loop_entrypoint(self) -> None:
        self._state.mark(ServicePhase.RUNNING)
        self._log("Loop entered; processing iterations")
        try:
            while not self._stop_event.is_set():
                try:
                    self._execute_iteration(**self._loop_iteration_kwargs())
                except Exception as exc:  # pragma: no cover - surfaced via logs
                    self._handle_iteration_error(exc)
                    if self._stop_event.wait(self._error_backoff):
                        break
                    # Expose that the loop recovered from an error without dropping
                    # the previous error message.
                    self._state.mark(ServicePhase.RUNNING, error=self._state.last_error)
                    continue

                if self._loop_delay and self._stop_event.wait(self._loop_delay):
                    break
        finally:
            self._stop_event.clear()
            self._state.mark(ServicePhase.STOPPED)
            self._log("Loop stopped")
            self._on_loop_stopped()

    def _execute_iteration(self, **kwargs: Any) -> Dict[str, Any]:
        iteration_number = self._state.iterations + 1
        self._log(f"Iteration {iteration_number} started")
        try:
            result = self._run_iteration(**kwargs)
            self._state.increment_iterations()
            self._log(f"Iteration {iteration_number} completed")
            return result
        except Exception as exc:
            self._state.mark(ServicePhase.ERROR, error=str(exc))
            self._log(f"Iteration {iteration_number} failed: {exc}")
            raise

    def _loop_iteration_kwargs(self) -> Dict[str, Any]:
        """Override to inject kwargs for background iterations."""

        return {}

    @abstractmethod
    def _run_iteration(self, **kwargs: Any) -> Dict[str, Any]:
        """Concrete services must implement one unit of work."""

    def _handle_iteration_error(self, exc: Exception) -> None:
        self._log(f"Error during iteration: {exc}")

    def _on_loop_stopped(self) -> None:
        """Hook for subclasses to release resources when the loop exits."""

        return None

    def _log(self, message: str) -> None:
        print(f"[{self.__class__.__name__}] {message}")
