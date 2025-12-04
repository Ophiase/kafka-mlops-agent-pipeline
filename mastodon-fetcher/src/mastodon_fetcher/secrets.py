import os
from os.path import join
from typing import Optional

# Paths
SECRET_FOLDER = "/secrets"
MASTODON_ACCESS_TOKEN_PATH = join(SECRET_FOLDER, "MASTODON_ACCESS_TOKEN")

# Constants
MASTODON_ACCESS_TOKEN = None


def try_read_file(file_path: str) -> Optional[str]:
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return None


def populate_constants() -> None:
    if not os.path.exists(SECRET_FOLDER):
        print(f"Warning: Secret folder '{SECRET_FOLDER}' does not exist.")
        return

    global MASTODON_ACCESS_TOKEN
    MASTODON_ACCESS_TOKEN = try_read_file(MASTODON_ACCESS_TOKEN_PATH)
