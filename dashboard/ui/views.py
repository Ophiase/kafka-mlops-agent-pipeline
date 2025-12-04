from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Sequence

from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .services import ControlApiClient, ControlApiError


def _positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise ValueError
    return number


def _non_negative_float(value: str) -> float:
    number = float(value)
    if number < 0:
        raise ValueError
    return number


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "on", "yes"}


@dataclass(frozen=True)
class ConfigField:
    name: str
    label: str
    parser: Callable[[str], Any]
    input_type: str = "number"
    min_value: str | None = None
    step: str | None = None
    metadata_key: str | None = None


def _fetcher_metrics(metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {"label": "Last Fetch Size", "value": metadata.get("fetched")},
        {"label": "Sent to Kafka", "value": metadata.get("sent_to_kafka")},
        {"label": "Default Limit", "value": metadata.get("fetch_limit")},
        {"label": "Loop Delay (s)", "value": metadata.get("loop_delay")},
    ]


def _processor_metrics(metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {"label": "Received", "value": metadata.get("received")},
        {"label": "Processed", "value": metadata.get("processed")},
        {"label": "Sent", "value": metadata.get("sent")},
        {"label": "Max Records", "value": metadata.get("max_records")},
        {"label": "Timeout (ms)", "value": metadata.get("timeout_ms")},
    ]


SERVICE_DEFINITIONS = {
    "fetcher": {
        "label": "Mastodon Fetcher",
        "setting": "FETCHER_API_URL",
        "supports_limit": True,
        "metrics_builder": _fetcher_metrics,
        "config_fields": (
            ConfigField("fetch_limit", "Fetch limit", _positive_int, min_value="1"),
            ConfigField(
                "loop_delay",
                "Loop delay (s)",
                _non_negative_float,
                step="0.1",
                min_value="0",
            ),
        ),
    },
    "processor": {
        "label": "Metrics Processor",
        "setting": "PROCESSOR_API_URL",
        "supports_limit": False,
        "metrics_builder": _processor_metrics,
        "config_fields": (
            ConfigField("timeout_ms", "Timeout (ms)", _positive_int, min_value="1"),
            ConfigField("max_records", "Max records", _positive_int, min_value="1"),
        ),
    },
}


def _build_clients() -> Dict[str, ControlApiClient]:
    return {
        key: ControlApiClient(getattr(settings, definition["setting"]))
        for key, definition in SERVICE_DEFINITIONS.items()
    }


def dashboard(request: HttpRequest) -> HttpResponse:
    clients = _build_clients()

    if request.method == "POST":
        _handle_post(request, clients)
        return redirect("dashboard")

    services = _build_service_context(clients)
    return render(request, "dashboard.html", {"services": services})


def _handle_post(request: HttpRequest, clients: Dict[str, ControlApiClient]) -> None:
    service_key = (request.POST.get("service") or "").strip()
    action = (request.POST.get("action") or "").strip()
    definition = SERVICE_DEFINITIONS.get(service_key)
    client = clients.get(service_key)

    if not definition or not client or not action:
        messages.error(request, "Unknown service or action.")
        return

    try:
        if action == "start":
            client.start()
            messages.success(request, f"{definition['label']} started.")
        elif action == "stop":
            client.stop()
            messages.info(request, f"{definition['label']} stopping...")
        elif action == "run":
            payload = _build_run_payload(request, definition)
            client.run(payload)
            messages.success(request, f"{definition['label']} executed one iteration.")
        elif action == "configure":
            payload = _build_config_payload(request, definition.get("config_fields", ()))
            client.configure(payload)
            messages.success(request, f"{definition['label']} configuration updated.")
        else:
            messages.error(request, f"Unsupported action '{action}'.")
    except ValueError as exc:
        messages.error(request, str(exc) or "Invalid input provided.")
    except ControlApiError as exc:
        messages.error(request, f"{definition['label']} error: {exc}")


def _build_run_payload(request: HttpRequest, definition: Dict[str, Any]) -> Dict[str, Any]:
    payload = {"send_to_kafka": _parse_bool(request.POST.get("send_to_kafka"), default=True)}

    if definition.get("supports_limit"):
        limit_raw = (request.POST.get("limit") or "").strip()
        if limit_raw:
            payload["limit"] = _positive_int(limit_raw)
    return payload


def _build_config_payload(request: HttpRequest, fields: Sequence[ConfigField]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}

    for field in fields:
        raw = (request.POST.get(field.name) or "").strip()
        if not raw:
            continue
        try:
            payload[field.name] = field.parser(raw)
        except ValueError as exc:  # pragma: no cover - user error surface via message
            raise ValueError(f"{field.label} must be a valid number.") from exc

    if not payload:
        raise ValueError("Provide at least one configuration value.")
    return payload


def _build_service_context(clients: Dict[str, ControlApiClient]) -> List[Dict[str, Any]]:
    services: List[Dict[str, Any]] = []

    for key, definition in SERVICE_DEFINITIONS.items():
        client = clients[key]
        try:
            state = client.state()
        except ControlApiError as exc:
            state = {
                "phase": "offline",
                "iterations": 0,
                "last_error": str(exc),
                "metadata": {},
            }

        metadata = state.get("metadata") or {}
        config_fields = [
            {
                "name": field.name,
                "label": field.label,
                "input_type": field.input_type,
                "min": field.min_value,
                "step": field.step,
                "value": metadata.get(field.metadata_key or field.name),
            }
            for field in definition.get("config_fields", ())
        ]

        services.append(
            {
                "key": key,
                "label": definition["label"],
                "phase": state.get("phase", "unknown"),
                "iterations": state.get("iterations", 0),
                "last_error": state.get("last_error"),
                "metadata": metadata,
                "metrics": definition["metrics_builder"](metadata),
                "supports_limit": definition.get("supports_limit", False),
                "config_fields": config_fields,
            }
        )

    return services
