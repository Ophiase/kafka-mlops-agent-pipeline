import datetime
import json
from typing import Any, Dict, List

from kafka import KafkaProducer

from shared.kafka.constants import KAFKA_PORT, KAFKA_PROCESSED_TOPIC, KAFKA_SERVER


class Sender:
    def __init__(self, bootstrap_servers: str = f"{KAFKA_SERVER}:{KAFKA_PORT}") -> None:
        print(bootstrap_servers)
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(
                v, default=self.json_serializer
            ).encode("utf-8"),
        )

    def __call__(self, informations: List[Dict[str, Any]]) -> None:
        self.send_posts(informations)

    def send_posts(self, informations: List[Dict[str, Any]]) -> None:
        print(f"Sending {len(informations)} informations to Kafka...")
        for information in informations:
            self.producer.send(KAFKA_PROCESSED_TOPIC, information)
        self.producer.flush()
        print(f"Sent {len(informations)} informations to Kafka")

    def json_serializer(self, obj: Any) -> str:
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
