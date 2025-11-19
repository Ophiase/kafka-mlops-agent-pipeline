import logging
from typing import Dict, List, Any
from mastodon import Mastodon
from constants import FETCH_NUMBER, FETCH_INTERVAL_MS


class Fetcher:
    def __init__(self, token: str = None):
        API_BASE_URL = "https://mastodon.social"

        self.token = token
        self.client = Mastodon(
            api_base_url=API_BASE_URL,
            access_token=token
        )

    def __call__(self, limit: int = FETCH_NUMBER) -> List[Dict[str, Any]]:
        logging.info(f"Fetching {limit} public posts from Mastodon")
        raw_posts = self.fetch_public(limit, self.client)
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
