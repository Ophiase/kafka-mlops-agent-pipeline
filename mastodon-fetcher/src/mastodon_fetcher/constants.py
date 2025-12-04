from os import environ

FETCH_INTERVAL_MS = int(environ.get("FETCH_INTERVAL_MS", 10 * 1000))
FETCH_NUMBER = int(environ.get("FETCH_NUMBER", 20))
