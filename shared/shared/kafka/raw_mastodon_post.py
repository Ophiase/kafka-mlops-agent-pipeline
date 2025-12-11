from typing import TypedDict


class RawMastodonPost(TypedDict):
    id: int
    created: str
    author: str
    text: str
    tags: list[str]
    url: str