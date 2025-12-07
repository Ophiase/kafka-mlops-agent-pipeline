from metrics_processor.processor import Processor


def build_processor() -> Processor:
    """
    I run those tests outside of the Docker container, so I need to point to localhost (instead of llm-server).
    """
    print("Building Processor for localhost test ...")
    OLLAMA_SERVER_URL = "localhost"
    OLLAMA_SERVER_PORT = 11434
    return Processor(base_url=f"http://{OLLAMA_SERVER_URL}:{OLLAMA_SERVER_PORT}")
