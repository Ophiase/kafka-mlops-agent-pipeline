import os

FETCH_INTERVAL_MS = int(os.environ.get("FETCH_INTERVAL_MS", 10 * 1000))
FETCH_NUMBER = int(os.environ.get("FETCH_NUMBER", 20))

KAFKA_SERVER = os.environ.get("KAFKA_SERVER", "kafka")
KAFKA_PORT = int(os.environ.get("KAFKA_PORT", 9092))
KAFKA_RAW_TOPIC = os.environ.get("KAFKA_RAW_TOPIC", "mastodon_raw_posts")