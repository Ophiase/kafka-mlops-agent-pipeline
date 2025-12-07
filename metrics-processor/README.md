# Metrics Processor

This module is responsible for processing and aggregating metrics data from posts coming through the Kafka topics. It then forwards the processed metrics to the designated output Kafka topic for further analysis or storage.

The main component is the `processor.py` class. It creates a processing **langgraph** pipeline that ingests raw metrics data, performs necessary computations, and outputs the aggregated results. 

It consists of three main nodes:
- `pre_processor.py`: Cleans and formats the incoming raw metrics data.
- `generator.py`: Uses an llm model to analyze the metrics and extract insights.
- `post_processor.py`: Aggregates the processed data and prepares it for output.

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
uv sync --refresh # to force reinstallation of dependencies without cache

# CLI mode
uv run -m src.metrics_processor.main

# Exposed api mode (for dashboard integration)
uv run uvicorn src.metrics_processor.api:app --host localhost --port 8002

# Test the workflow on test data
# It can directly be executed on the host without Kafka and Docker
uv run -m tests.test_inference
```
