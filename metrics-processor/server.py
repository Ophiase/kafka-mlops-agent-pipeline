# from processor import Processor
from kafka import KafkaConsumer
from constants import KAFKA_PORT, KAFKA_PROCESSED_TOPIC, KAFKA_RAW_TOPIC, KAFKA_SERVER


class Server:
    consumer: KafkaConsumer
    # processor: Processor

    def __init__(self):
        print(
            f"Arguments: {KAFKA_SERVER}:{KAFKA_PORT}, topic={KAFKA_RAW_TOPIC}")

        self.consumer = KafkaConsumer(
            KAFKA_RAW_TOPIC,
            bootstrap_servers=f"{KAFKA_SERVER}:{KAFKA_PORT}",
            auto_offset_reset='earliest')

        # self.processor = Processor()

    def run(self):
        print("Metrics Processor Server is Listening...")

        # test_string = "Hello, world! who are you?"
        # response = self.processor(test_string)
        # print("Response:", response)

        for message in self.consumer:
            print("Received message:", message.value.decode('utf-8'))
            # processed = self.processor(message.value.decode('utf-8'))
