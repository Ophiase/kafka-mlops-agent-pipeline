from processor import Processor
from kafka import KafkaConsumer
from constants import KAFKA_PORT, KAFKA_PROCESSED_TOPIC, KAFKA_RAW_TOPIC, KAFKA_SERVER
from constants import OLLAMA_MODEL, OLLAMA_SERVER_URL, OLLAMA_SERVER_PORT


class Server:
    # consumer: KafkaConsumer
    processor: Processor

    def __init__(self):
        # self.consumer = KafkaConsumer(
        #     KAFKA_RAW_TOPIC,
        #     bootstrap_servers=f"{KAFKA_SERVER}:{KAFKA_PORT}",
        #     auto_offset_reset='earliest')

        self.processor = Processor(
            model=OLLAMA_MODEL,
            base_url=f"http://{OLLAMA_SERVER_URL}:{OLLAMA_SERVER_PORT}"
        )

        prompts = [
            "I love the new design of your website!",
            "The product quality has significantly improved over the years.",
            "Customer service was unhelpful and rude.",
            "I'm extremely satisfied with my purchase experience.",
            "The delivery was delayed and the package arrived damaged."
        ]

        result = self.processor(prompts)
        print(result)

    def run(self):
        print("Metrics Processor Server is Listening...")

        # test_string = "Hello, world! who are you?"
        # response = self.processor([test_string])
        # print("Response:", response)

        # for message in self.consumer:
        #     print("Received message:", message.value.decode('utf-8'))
        #     processed = self.processor([message.value.decode('utf-8')])
        #     print("Processed:", processed)
