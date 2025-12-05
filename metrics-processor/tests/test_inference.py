from .dummy_posts import *


def build_posts_xy():
    return [
        (POST_00, POST_LABEL_00),
        (POST_01, POST_LABEL_01),
        (POST_02, POST_LABEL_02),
        (POST_03, POST_LABEL_03),
    ]


def verify_post(post: dict, expected_label: str):
    label = ""


def main():
    posts_xy = build_posts_xy()
    for post, label in posts_xy:
        print("POST:", post)
        print("LABEL:", label)
        print()


if __name__ == "__main__":
    main()
