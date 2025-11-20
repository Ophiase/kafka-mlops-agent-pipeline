from os import environ

FETCH_INTERVAL_MS = int(environ.get("FETCH_INTERVAL_MS", 10 * 1000))
FETCH_NUMBER = int(environ.get("FETCH_NUMBER", 20))

KAFKA_SERVER = environ.get("KAFKA_SERVER", "kafka")
KAFKA_PORT = int(environ.get("KAFKA_PORT", 9092))
KAFKA_RAW_TOPIC = environ.get("KAFKA_RAW_TOPIC", "mastodon_raw_posts")