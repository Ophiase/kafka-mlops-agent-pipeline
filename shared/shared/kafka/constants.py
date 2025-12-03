from os import environ

KAFKA_SERVER = environ.get("KAFKA_SERVER", "kafka")
KAFKA_PORT = int(environ.get("KAFKA_PORT", 9092))

KAFKA_RAW_TOPIC = environ.get("KAFKA_RAW_TOPIC", "mastodon_raw_posts")
KAFKA_PROCESSED_TOPIC = environ.get("KAFKA_PROCESSED_TOPIC", "processed_posts")
