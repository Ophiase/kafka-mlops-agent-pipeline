import os

FETCH_INTERVAL_MS = int(os.environ.get("FETCH_INTERVAL_MS", 10 * 1000))
FETCH_NUMBER = int(os.environ.get("FETCH_NUMBER", 20))