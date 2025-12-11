from typing import Any, Dict, List

from mastodon import Mastodon

from .constants import FETCH_NUMBER


class Fetcher:
    def __init__(self, token: str | None = None) -> None:
        api_base_url = "https://mastodon.social"
        self.token = token
        self.client = Mastodon(api_base_url=api_base_url, access_token=token)

    def __call__(self, limit: int = FETCH_NUMBER) -> List[Dict[str, Any]]:
        print(f"Fetching {limit} public posts from Mastodon")
        raw_posts = self.fetch_public(limit, self.client)
        return self.extract(raw_posts)

    def fetch_public(
        self, limit: int, client: Mastodon | None = None
    ) -> List[Dict[str, Any]]:
        client = client or self.client
        return client.timeline_public(limit=limit)

    def extract(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                "id": post["id"],
                "created": post["created_at"],
                "author": post["account"]["acct"],
                "text": post["content"],
                "tags": [tag["name"] for tag in post["tags"]],
                "url": post["url"],
            }
            for post in posts
        ]

    def show(self, posts: List[Dict[str, Any]]) -> None:
        for post in posts:
            print(post["created"], post["author"], "-", post["text"], "\n")
