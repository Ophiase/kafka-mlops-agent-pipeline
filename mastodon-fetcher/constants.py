import os

FETCH_INTERVAL_MS = int(os.environ.get("FETCH_INTERVAL_MS", 60 * 1000))
