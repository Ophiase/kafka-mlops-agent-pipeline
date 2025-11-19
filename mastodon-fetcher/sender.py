from typing import Any, Dict, List


class Sender:
    def __init__(self):
        pass

    def __call__(self, posts: List[Dict[str, Any]], *args, **kwds):
        self.send_kafka(posts)

    def send_kafka(self, posts: List[Dict[str, Any]]) -> None:
        print(f"Sending {len(posts)} posts to Kafka...")
