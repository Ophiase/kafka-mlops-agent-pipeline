from secrets import MASTODON_ACCESS_TOKEN
from constants import FETCH_NUMBER, FETCH_INTERVAL_MS
from mastodon import Mastodon
from fetcher import Fetcher
from sender import Sender
from typing import List, Dict, Any
import time


class Server:
    def __init__(self):
        pass

    def run(self):
        fetcher = Fetcher(MASTODON_ACCESS_TOKEN)
        sender = Sender()

        while True:
            posts = fetcher()
            sender(posts)

            time.sleep(FETCH_INTERVAL_MS / 1000)
