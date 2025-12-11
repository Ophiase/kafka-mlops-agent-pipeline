from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List

from kafka import KafkaConsumer, TopicPartition

from shared.kafka.constants import (
    KAFKA_PORT,
    KAFKA_PROCESSED_TOPIC,
    KAFKA_RAW_TOPIC,
    KAFKA_SERVER,
)

TAIL_LIMIT = 10


@dataclass(slots=True)
class TailSample:
    partition: int
    offset: int
    timestamp: str
    value: str


def _prettify_payload(payload: bytes) -> str:
    text = payload.decode("utf-8", errors="replace")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return text.strip()
    return json.dumps(parsed, indent=2, sort_keys=True)


def _format_timestamp(epoch_millis: int | None) -> str:
    if epoch_millis is None:
        return ""
    dt = datetime.fromtimestamp(epoch_millis / 1000, tz=timezone.utc)
    return dt.isoformat()


def fetch_tail(
    topic: str,
    *,
    limit: int = TAIL_LIMIT,
    raise_on_error: bool = False,
) -> List[TailSample]:
    consumer: KafkaConsumer | None = None
    try:
        consumer = KafkaConsumer(
            bootstrap_servers=f"{KAFKA_SERVER}:{KAFKA_PORT}",
            enable_auto_commit=False,
            auto_offset_reset="latest",
            consumer_timeout_ms=250,
            security_protocol="PLAINTEXT",
        )

        partitions = consumer.partitions_for_topic(topic)
        if not partitions:
            return []

        assignments = [TopicPartition(topic, partition) for partition in partitions]
        consumer.assign(assignments)
        end_offsets = consumer.end_offsets(assignments)

        for tp in assignments:
            start_offset = max(end_offsets[tp] - limit, 0)
            consumer.seek(tp, start_offset)

        samples: List[TailSample] = []
        while len(samples) < limit:
            batch = consumer.poll(timeout_ms=200)
            if not batch:
                break
            for records in batch.values():
                for record in records:
                    samples.append(
                        TailSample(
                            partition=record.partition,
                            offset=record.offset,
                            timestamp=_format_timestamp(record.timestamp),
                            value=_prettify_payload(record.value),
                        )
                    )
        return samples[-limit:]
    finally:
        consumer.close()


def initial_tails(limit: int = TAIL_LIMIT) -> Dict[str, List[TailSample]]:
    return {
        "raw": fetch_tail(KAFKA_RAW_TOPIC, limit=limit),
        "processed": fetch_tail(KAFKA_PROCESSED_TOPIC, limit=limit),
    }
