from pprint import pprint
from typing import Dict, Any, List
from .dummy_posts import *
from metrics_processor.processor import Processor


def build_posts_xy():
    return [
        (POST_00, POST_LABEL_00),
        (POST_01, POST_LABEL_01),
        (POST_02, POST_LABEL_02),
        (POST_03, POST_LABEL_03),
    ]


def build_processor() -> Processor:
    print("Building Processor...")
    return Processor()


def verify_output(
        output: Dict[str, Any],
        expected_label: str) -> bool:
    return output["sentiment"] == expected_label


def verify_batch(
        processor: Processor,
        posts: List[Dict[str, Any]],
        expected_labels: List[Dict[str, str]]
) -> List[bool]:
    print("Verifying batch...")
    processed_outputs = processor(posts)
    print("Processed Outputs:")
    zipped = zip(processed_outputs, expected_labels)
    results = [
        verify_output(output, expected_label)
        for output, expected_label in zipped
    ]
    return results


def main():
    posts_xy = build_posts_xy()
    posts_x, posts_y = zip(*posts_xy)
    processor = build_processor()
    results = verify_batch(
        processor, posts_x, posts_y
    )

    pprint(results)


if __name__ == "__main__":
    main()
