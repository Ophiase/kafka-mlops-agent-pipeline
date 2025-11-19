from server import MastodonFetcherServer


def main():
    print("Starting Mastodon Fetcher Server...")
    MastodonFetcherServer().run()


if __name__ == "__main__":
    main()
