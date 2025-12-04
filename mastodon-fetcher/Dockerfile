FROM ghcr.io/astral-sh/uv:python3.12-bookworm

WORKDIR /app
COPY ./mastodon-fetcher /app
COPY ./shared /shared

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/src"
ENV UV_LINK_MODE=copy
ENV FETCHER_API_PORT=8001
RUN uv sync --frozen

# CMD ["tail", "-f", "/dev/null"]
CMD ["sh", "-c", "uv run uvicorn mastodon_fetcher.api:app --host 0.0.0.0 --port ${FETCHER_API_PORT:-8001}"]
