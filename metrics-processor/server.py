import json
from processor import Processor
from sender import Sender
from kafka import KafkaConsumer
from constants import KAFKA_PORT, KAFKA_PROCESSED_TOPIC, KAFKA_RAW_TOPIC, KAFKA_SERVER
from constants import OLLAMA_MODEL, OLLAMA_SERVER_URL, OLLAMA_SERVER_PORT
from typing import List, Dict, Any, Optional


class Server:
    consumer: KafkaConsumer
    processor: Processor
    sender: Sender

    timeout_ms: int
    max_records: int

    def __init__(self,
                 timeout_ms: int = 1000,
                 max_records: int = 5):
        self.timeout_ms = timeout_ms
        self.max_records = max_records

        self.consumer = KafkaConsumer(
            KAFKA_RAW_TOPIC,
            bootstrap_servers=f"{KAFKA_SERVER}:{KAFKA_PORT}",
            auto_offset_reset='earliest')

        self.processor = Processor(
            model=OLLAMA_MODEL,
            base_url=f"http://{OLLAMA_SERVER_URL}:{OLLAMA_SERVER_PORT}"
        )
        self.sender = Sender()

    def run(self):
        print("Metrics Processor Server is Listening...")

        while True:
            print("-" * 20)
            print("Polling for messages...")

            messages = self.pull_messages()
            if not messages:
                continue
            print(f"Received {len(messages)} messages")

            processed_messages = self.processor(messages)
            print(f"Processed {len(processed_messages)} messages")

            self.sender.send(processed_messages)
            print(f"Sent {len(processed_messages)} messages")

    def pull_messages(self) -> Optional[List[str]]:
        raw_messages = self.consumer.poll(
            timeout_ms=self.timeout_ms,
            max_records=self.max_records)

        if not raw_messages:
            return None

        n_messages = 0
        result: List[Dict[str, Any]] = []
        for topic_partition, kafka_messages in raw_messages.items():
            for kafka_message in kafka_messages:
                n_messages = n_messages + 1
                try:
                    message_string = kafka_message.value.decode()
                    decoded_data = json.loads(message_string)
                    result.append(decoded_data)
                except Exception as decode_error:
                    print("Error decoding message:", decode_error)

        if len(result) != n_messages:
            print(
                f"Warning: Expected {n_messages} messages, but decoded {len(result)}")

        return result
