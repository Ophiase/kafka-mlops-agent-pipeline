from __future__ import annotations

import json
import threading
from typing import Any, Dict, List, Optional

from kafka import KafkaConsumer

from shared.kafka.constants import KAFKA_PORT, KAFKA_RAW_TOPIC, KAFKA_SERVER
from shared.kafka.topics import ensure_topic_exists
from shared.server import BaseService

from .constants import (
    KAFKA_GROUP_ID,
    OLLAMA_MODEL,
    OLLAMA_SERVER_PORT,
    OLLAMA_SERVER_URL,
)
from .processor import Processor
from .sender import Sender


class Server(BaseService):
    processor: Processor
    sender: Sender

    def __init__(self, *, timeout_ms: int = 1000, max_records: int = 5):
        super().__init__(loop_delay=0.0)
        self.timeout_ms = timeout_ms
        self.max_records = max_records
        self._consumer: Optional[KafkaConsumer] = None
        self._consumer_owner: Optional[int] = None
        self.processor = Processor(
            model=OLLAMA_MODEL,
            base_url=f"http://{OLLAMA_SERVER_URL}:{OLLAMA_SERVER_PORT}",
        )
        self.sender = Sender()
        self._state.metadata.update(
            {
                "timeout_ms": self.timeout_ms,
                "max_records": self.max_records,
            }
        )

        ensure_topic_exists(
            bootstrap_servers=f"{KAFKA_SERVER}:{KAFKA_PORT}",
            topic_name=KAFKA_RAW_TOPIC,
            num_partitions=1,
            replication_factor=1,
        )

    def run(self) -> None:
        self._log("Metrics Processor Server is Listening...")
        self.start()
        self.wait()

    def configure(
        self, *, timeout_ms: Optional[int] = None, max_records: Optional[int] = None
    ) -> None:
        """
        Update the server configuration.
        """
        if timeout_ms is not None and timeout_ms > 0:
            self.timeout_ms = timeout_ms
        if max_records is not None and max_records > 0:
            self.max_records = max_records
        self._state.metadata.update(
            {
                "timeout_ms": self.timeout_ms,
                "max_records": self.max_records,
            }
        )

    def _loop_iteration_kwargs(self) -> Dict[str, Any]:
        return {"send_to_kafka": True}

    def _run_iteration(self, *, send_to_kafka: bool = True) -> Dict[str, Any]:
        """
        Execute a single processing iteration.
        Returns a snapshot of the iteration results.
        """
        release_after_iteration = not self.is_running
        consumer = self._acquire_consumer()
        try:
            # Pull messages from Kafka
            print("Pulling messages from Kafka...")
            raw_messages = self.pull_messages(consumer)
            if not raw_messages or len(raw_messages) == 0:
                self._log("No Kafka messages available on this iteration")
                snapshot = {
                    "received": 0,
                    "processed": 0,
                    "sent": 0,
                    "send_to_kafka": send_to_kafka,
                }
                self._state.metadata.update(snapshot)
                return {**snapshot, "messages": [], "processed_messages": []}

            # Process messages
            self._log(f"Processing {len(raw_messages)} message(s) via LLM")
            processed_messages = self.processor(raw_messages)

            # Send to Kafka
            if send_to_kafka and processed_messages:
                self.sender(processed_messages)
                self._log(
                    f"Sent {len(processed_messages)} processed message(s) to Kafka"
                )

            snapshot = {
                "received": len(raw_messages),
                "processed": len(processed_messages),
                "sent": len(processed_messages) if send_to_kafka else 0,
                "send_to_kafka": send_to_kafka,
            }
            self._state.metadata.update(snapshot)
            return {
                **snapshot,
                "messages": raw_messages,
                "processed_messages": processed_messages,
            }
        except Exception:
            # Force consumer recreation on next iteration after any failure.
            self._release_consumer()
            raise
        finally:
            if release_after_iteration:
                self._release_consumer()

    def show_offsets(self, consumer: KafkaConsumer) -> None:
        for tp in consumer.assignment():
            position = consumer.position(tp)
            self._log(f"TopicPartition {tp} at offset {position}")

    def pull_messages(self, consumer: KafkaConsumer) -> Optional[List[Dict[str, Any]]]:
        self.show_offsets(consumer)
        raw_messages = consumer.poll(
            timeout_ms=self.timeout_ms,
            max_records=self.max_records,
        )
        self.show_offsets(consumer)

        if not raw_messages:
            self._log("Kafka consumer poll returned no messages")
            return None

        n_messages = 0
        result: List[Dict[str, Any]] = []
        for topic_partition, kafka_messages in raw_messages.items():
            for kafka_message in kafka_messages:
                n_messages += 1
                try:
                    message_string = kafka_message.value.decode()
                    decoded_data = json.loads(message_string)
                    result.append(decoded_data)
                except Exception as decode_error:
                    print("Error decoding message:", decode_error)

        if len(result) != n_messages:
            self._log(
                f"Warning: Expected {n_messages} messages, but decoded {len(result)}"
            )

        if result:
            self._log(f"Kafka consumer delivered {len(result)} message(s)")
        else:
            self._log("Kafka consumer poll returned empty payload")

        return result

    def _acquire_consumer(self) -> KafkaConsumer:
        caller = threading.get_ident()
        if self._consumer is None:
            self._consumer = KafkaConsumer(
                KAFKA_RAW_TOPIC,
                bootstrap_servers=f"{KAFKA_SERVER}:{KAFKA_PORT}",
                group_id=KAFKA_GROUP_ID,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
            )
            self._consumer_owner = caller
        elif self._consumer_owner != caller:
            raise RuntimeError(
                "KafkaConsumer is tied to the running loop; stop it before running a manual iteration."
            )
        return self._consumer

    def _release_consumer(self) -> None:
        if self._consumer is None:
            return
        self._consumer.close()
        self._consumer = None
        self._consumer_owner = None

    def _on_loop_stopped(self) -> None:
        self._release_consumer()
