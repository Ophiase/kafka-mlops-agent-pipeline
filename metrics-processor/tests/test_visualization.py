import os
from os.path import abspath, dirname, join

from src.metrics_processor.processor import Processor

from .utils import build_processor


def test_visualization():
    print("Initializing Processor...")
    # We can use dummy values since we just want the graph structure
    processor = build_processor()

    print("Generating graph visualization...")
    try:
        # Try to get the graph object
        graph = processor.graph.get_graph()

        # Try to generate mermaid PNG
        # This requires 'langgraph' and potentially 'pygraphviz' or similar depending on the version,
        # but draw_mermaid_png is the standard way now.
        png_bytes = graph.draw_mermaid_png()

        output_path = join("resources", "workflow_graph.png")
        with open(output_path, "wb") as f:
            f.write(png_bytes)

        print(f"Graph visualization saved to {abspath(output_path)}")

    except Exception as e:
        print(f"Failed to generate visualization: {e}")


if __name__ == "__main__":
    test_visualization()
