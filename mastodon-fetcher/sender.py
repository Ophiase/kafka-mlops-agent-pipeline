from kafka import KafkaProducer
from typing import Any, Dict, List
from constants import KAFKA_SERVER, KAFKA_PORT, KAFKA_RAW_TOPIC
import json


class Sender:
    def __init__(self, bootstrap_servers: str = f"{KAFKA_SERVER}:{KAFKA_PORT}") -> None:
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def __call__(self, posts: List[Dict[str, Any]]) -> None:
        self.send_posts(posts)

    def send_posts(self, posts: List[Dict[str, Any]]) -> None:
        print(f"Sending {len(posts)} posts to Kafka...")
        for post in posts:
            self.send(KAFKA_RAW_TOPIC, post)

    def send(self, topic: str, message: Dict[str, Any]) -> None:
        self.producer.send(topic, message)
        self.producer.flush()
