from os import environ


OLLAMA_SERVER_URL = environ.get("OLLAMA_SERVER_URL", "llm-server")
OLLAMA_SERVER_PORT = environ.get("OLLAMA_SERVER_PORT", "11434")
OLLAMA_MODEL = environ.get("OLLAMA_MODEL", "qwen3:0.6b")
