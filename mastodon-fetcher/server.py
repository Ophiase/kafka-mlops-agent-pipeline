from secrets import MASTODON_ACCESS_TOKEN

class MastodonFetcherServer:
    def run(self):
        print("Server is running")
        print("Using access token:", MASTODON_ACCESS_TOKEN)