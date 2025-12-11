from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, List, Sequence
from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET
from .services import ControlApiClient, ControlApiError
from .kafka_tail import TailSample, initial_tails, fetch_tail, TAIL_LIMIT
from shared.kafka.constants import KAFKA_PROCESSED_TOPIC, KAFKA_RAW_TOPIC


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
        {"label": "Sent to Kafka (total)", "value": metadata.get("sent_to_kafka")},
        {"label": "Last Batch Sent", "value": metadata.get("last_sent")},
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
        "kafka_stream": "raw",
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
        "kafka_stream": "processed",
        "config_fields": (
            ConfigField("timeout_ms", "Timeout (ms)", _positive_int, min_value="1"),
            ConfigField("max_records", "Max records", _positive_int, min_value="1"),
        ),
    },
}

KAFKA_PANEL_TITLES = {
    "raw": "Raw Kafka Stream Tail",
    "processed": "Processed Kafka Stream Tail",
}


def _build_clients() -> Dict[str, ControlApiClient]:
    return {
        key: ControlApiClient(getattr(settings, definition["setting"]))
        for key, definition in SERVICE_DEFINITIONS.items()
    }


def dashboard(request: HttpRequest) -> HttpResponse:
    clients = _build_clients()
    kafka_urls = {
        "raw": reverse("kafka-tail", kwargs={"stream": "raw"}),
        "processed": reverse("kafka-tail", kwargs={"stream": "processed"}),
    }
    serialized_tails = {
        key: _serialize_tail(samples) for key, samples in initial_tails().items()
    }

    if request.method == "POST":
        _handle_post(request, clients)
        return redirect("dashboard")

    services = _build_service_context(clients, serialized_tails, kafka_urls)
    service_lookup = {service["key"]: service for service in services}
    context = {
        "services": services,
        "service_lookup": service_lookup,
        "kafka_urls": kafka_urls,
        "state_url": reverse("service-state"),
    }
    return render(request, "dashboard.html", context)


@require_GET
def service_state(request: HttpRequest) -> JsonResponse:
    clients = _build_clients()
    kafka_urls = {
        "raw": reverse("kafka-tail", kwargs={"stream": "raw"}),
        "processed": reverse("kafka-tail", kwargs={"stream": "processed"}),
    }
    services = _build_service_context(clients, {}, kafka_urls)
    return JsonResponse({"services": services})


TAIL_TOPIC_MAP = {
    "raw": KAFKA_RAW_TOPIC,
    "processed": KAFKA_PROCESSED_TOPIC,
}


@require_GET
def kafka_tail(request: HttpRequest, stream: str) -> JsonResponse:
    topic = TAIL_TOPIC_MAP.get(stream)
    if not topic:
        return JsonResponse({"error": "Unknown stream"}, status=404)

    try:
        limit = int(request.GET.get("limit", TAIL_LIMIT))
    except ValueError:
        limit = TAIL_LIMIT

    limit = max(1, min(limit, 100))

    try:
        samples = fetch_tail(topic, limit=limit, raise_on_error=True)
    except Exception as exc:  # pragma: no cover - observational logging surface
        return JsonResponse({"error": str(exc)}, status=502)

    return JsonResponse({
        "stream": stream,
        "messages": [_serialize_tail_entry(sample) for sample in samples],
    })


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


def _build_service_context(
    clients: Dict[str, ControlApiClient],
    kafka_tails: Dict[str, List[Dict[str, Any]]],
    kafka_urls: Dict[str, str],
) -> List[Dict[str, Any]]:
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

        stream = definition.get("kafka_stream")
        kafka_panel = None
        if stream:
            kafka_panel = {
                "stream": stream,
                "title": KAFKA_PANEL_TITLES.get(stream, f"{definition['label']} Kafka Tail"),
                "url": kafka_urls.get(stream, ""),
                "samples": kafka_tails.get(stream, []),
            }

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
                "kafka_panel": kafka_panel,
            }
        )

    return services


def _serialize_tail(samples: Sequence[TailSample]) -> List[Dict[str, Any]]:
    return [_serialize_tail_entry(sample) for sample in samples]


def _serialize_tail_entry(sample: TailSample) -> Dict[str, Any]:
    return asdict(sample)
