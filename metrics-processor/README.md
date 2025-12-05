# Metrics Processor

This module is responsible for processing and aggregating metrics data from posts coming through the Kafka topics. It then forwards the processed metrics to the designated output Kafka topic for further analysis or storage.

## Setup

### Kafka Server

You need to setup the following variables in your environment:
- `KAFKA_SERVER`
- `KAFKA_PORT`
- `KAFKA_RAW_TOPIC`
- `KAFKA_PROCESSED_TOPIC`
You can see the default values in `constants.py`.

### Ollama Server

You need to setup an Ollama server accessible from the module.

You need to setup the following variables in your environment:
- `OLLAMA_SERVER_URL`
- `OLLAMA_SERVER_PORT`
- `OLLAMA_MODEL`

You can see the default values in `constants.py`.

## Quickstart

```bash
uv sync
# cli mode
uv run src.metrics_processor.main
# exposed api mode (for dashboard integration)
uv run uvicorn src.metrics_processor.api:app --host localhost --port 8002
```