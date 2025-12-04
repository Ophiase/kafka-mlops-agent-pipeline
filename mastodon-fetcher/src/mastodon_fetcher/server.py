from __future__ import annotations
from typing import Any, Dict, Optional
from shared.server import BaseService
from .constants import FETCH_INTERVAL_MS, FETCH_NUMBER
from .fetcher import Fetcher
from .secrets import MASTODON_ACCESS_TOKEN
from .sender import Sender

DEFAULT_LOOP_DELAY = FETCH_INTERVAL_MS / 1000


class Server(BaseService):
    fetcher: Fetcher
    sender: Sender

    def __init__(self,
                 *,
                 access_token: Optional[str] = MASTODON_ACCESS_TOKEN,
                 fetch_limit: int = FETCH_NUMBER,
                 loop_delay: float = DEFAULT_LOOP_DELAY):
        super().__init__(loop_delay=loop_delay)
        self.fetcher = Fetcher(access_token)
        self.sender = Sender()
        self._default_limit = fetch_limit
        self._state.metadata.update({
            "fetch_limit": self._default_limit,
            "loop_delay": self._loop_delay,
        })

    def run(self) -> None:
        self.start()
        self.wait()

    def configure(self,
                  *,
                  fetch_limit: Optional[int] = None,
                  loop_delay: Optional[float] = None) -> None:
        if fetch_limit is not None and fetch_limit > 0:
            self._default_limit = fetch_limit
        if loop_delay is not None:
            self._loop_delay = max(0.0, loop_delay)
        self._state.metadata.update({
            "fetch_limit": self._default_limit,
            "loop_delay": self._loop_delay,
        })

    def _loop_iteration_kwargs(self) -> Dict[str, Any]:
        return {
            "limit": self._default_limit,
            "send_to_kafka": True,
        }

    def _run_iteration(self,
                       *,
                       limit: Optional[int] = None,
                       send_to_kafka: bool = True) -> Dict[str, Any]:
        limit = limit or self._default_limit
        posts = self.fetcher(limit=limit)
        if send_to_kafka and posts:
            self.sender(posts)
        metadata = {
            "limit": limit,
            "fetched": len(posts),
            "sent_to_kafka": len(posts) if send_to_kafka else 0,
            "send_to_kafka": send_to_kafka,
        }
        self._state.metadata.update(metadata)
        return {**metadata, "posts": posts}
