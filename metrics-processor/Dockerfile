FROM ghcr.io/astral-sh/uv:python3.12-bookworm

WORKDIR /app
COPY ./metrics-processor /app
COPY ./shared /shared

ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy
ENV PROCESSOR_API_PORT=8002
RUN uv sync --frozen

# CMD ["tail", "-f", "/dev/null"]
CMD ["sh", "-c", "uv run uvicorn api:app --host 0.0.0.0 --port ${PROCESSOR_API_PORT:-8002}"]
