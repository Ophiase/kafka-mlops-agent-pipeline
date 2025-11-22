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
uv sync
uv run main.py
```