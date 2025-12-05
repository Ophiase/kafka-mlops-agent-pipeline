# Mastodon Fetcher

A simple Mastodon to Kafka fetcher written in python.

## Setup

### Mastodon Key (optional)

Put your secret key in a secret file.
By default `secrets.py` uses a mounted:
- `/secrets/MASTODON_ACCESS_TOKEN`.

### Kafka Server

You need to setup the following variables in your environment:
- `KAFKA_SERVER`
- `KAFKA_PORT`
- `KAFKA_TOPIC`

You can see the default values in `constants.py`.

## Quickstart

```bash
# compile the environment
uv sync
# classic run
uv run src.mastodon_fetcher.main
# or run the exposed API
uv run uvicorn src.mastodon_fetcher.api:app --host 0.0.0.0 --port ${FETCHER_API_PORT:-8001}
```