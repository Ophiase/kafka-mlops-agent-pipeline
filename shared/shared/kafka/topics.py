from kafka.admin import KafkaAdminClient, NewTopic


def ensure_topic_exists(
    bootstrap_servers: str,
    topic_name: str,
    num_partitions: int = 1,
    replication_factor: int = 1,
):
    admin = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
    existing_topics = admin.list_topics()
    if topic_name not in existing_topics:
        topic = NewTopic(
            name=topic_name,
            num_partitions=num_partitions,
            replication_factor=replication_factor,
        )
        admin.create_topics([topic])
        print(f"Created topic: {topic_name}")
    else:
        print(f"Topic already exists: {topic_name}")
