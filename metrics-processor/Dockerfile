FROM ghcr.io/astral-sh/uv:python3.14-bookworm

WORKDIR /app
COPY . .

# CMD ["tail", "-f", "/dev/null"]
CMD ["sh", "-c", "uv sync && uv run main.py"]
