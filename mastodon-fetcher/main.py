from server import Server


def main():
    print("Starting Mastodon Fetcher Server...")
    print("-" * 20)
    Server().run()


if __name__ == "__main__":
    main()
