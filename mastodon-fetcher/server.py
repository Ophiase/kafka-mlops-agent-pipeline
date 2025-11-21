from secrets import MASTODON_ACCESS_TOKEN
from constants import FETCH_NUMBER, FETCH_INTERVAL_MS
from mastodon import Mastodon
from fetcher import Fetcher
from sender import Sender
from typing import List, Dict, Any
import time


class Server:
    fetcher: Fetcher
    sender: Sender

    def __init__(self):
        self.fetcher = Fetcher(MASTODON_ACCESS_TOKEN)
        self.sender = Sender()

    def run(self):

        while True:
            posts = self.fetcher()
            self.sender(posts)

            time.sleep(FETCH_INTERVAL_MS / 1000)
