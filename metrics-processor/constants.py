from os import environ


OLLAMA_SERVER_URL = environ.get("OLLAMA_SERVER_URL", "llm-server")
OLLAMA_SERVER_PORT = environ.get("OLLAMA_SERVER_PORT", "11434")
OLLAMA_MODEL = environ.get("OLLAMA_MODEL", "qwen3:0.6b")


KAFKA_SERVER = environ.get("KAFKA_SERVER", "kafka")
KAFKA_PORT = int(environ.get("KAFKA_PORT", 9092))

KAFKA_RAW_TOPIC = environ.get("KAFKA_RAW_TOPIC", "mastodon_raw_posts")
KAFKA_PROCESSED_TOPIC = environ.get("KAFKA_PROCESSED_TOPIC", "processed_posts")
