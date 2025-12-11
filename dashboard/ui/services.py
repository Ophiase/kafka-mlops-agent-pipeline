from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


class ControlApiError(RuntimeError):
    """Raised when the control API cannot be reached or returns an error."""


@dataclass
class ControlApiClient:
    base_url: str
    timeout: float = 10.0

    def _request(
        self, method: str, path: str, *, json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}{path}"
        try:
            response = requests.request(method, url, json=json, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:  # pragma: no cover - network errors
            raise ControlApiError(f"{method} {url} failed: {exc}") from exc

        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError as exc:  # pragma: no cover - invalid payloads
            raise ControlApiError(f"{method} {url} returned invalid JSON") from exc

    def state(self) -> Dict[str, Any]:
        return self._request("GET", "/state")

    def start(self) -> Dict[str, Any]:
        return self._request("POST", "/start")

    def stop(self) -> Dict[str, Any]:
        return self._request("POST", "/stop")

    def run(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request("POST", "/run", json=payload or {})

    def configure(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request("POST", "/configure", json=payload or {})
