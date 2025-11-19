from secrets import MASTODON_ACCESS_TOKEN
from constants import FETCH_NUMBER, FETCH_INTERVAL_MS
from mastodon import Mastodon
from typing import List, Dict, Any
import time


class MastodonFetcherServer:
    def __init__(self):
        pass

    def run(self):
        client = self.create_client(MASTODON_ACCESS_TOKEN)

        while True:
            posts = self.fetch(client)
            self.send_kafka(posts)

            time.sleep(FETCH_INTERVAL_MS / 1000)

    def create_client(self, token: str = None) -> Mastodon:
        return Mastodon(
            api_base_url="https://mastodon.social",
            access_token=token
        )

    def fetch(self, client: Mastodon) -> List[Dict[str, Any]]:
        raw_posts = self.fetch_public(FETCH_NUMBER, client)
        posts = self.extract(raw_posts)
        return posts

    def fetch_public(self, limit: int, client: Mastodon = None) -> List[Dict[str, Any]]:
        client = client or self.create_client()
        return client.timeline_public(limit=limit)

    def extract(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                "id": post["id"],
                "created": post["created_at"],
                "author": post["account"]["acct"],
                "text": post["content"],
                "tags": [tag["name"] for tag in post["tags"]],
                "url": post["url"]
            }
            for post in posts
        ]

    def show(self, posts: List[Dict[str, Any]]) -> None:
        def print_post(post: Dict[str, Any]) -> None:
            print(post["created"], post["author"], "-", post["text"], "\n")

        for post in posts:
            print_post(post)

    def send_kafka(self, posts: List[Dict[str, Any]]) -> None:
        # Placeholder for Kafka sending logic
        self.show(posts)
