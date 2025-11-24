FROM ghcr.io/astral-sh/uv:python3.12-bookworm

WORKDIR /app
COPY . .

ENV PYTHONUNBUFFERED=1

# CMD ["tail", "-f", "/dev/null"]
CMD ["sh", "-c", "uv sync && uv run main.py"]
