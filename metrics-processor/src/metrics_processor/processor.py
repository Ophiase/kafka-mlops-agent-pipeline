from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph

from .constants import OLLAMA_MODEL, OLLAMA_SERVER_PORT, OLLAMA_SERVER_URL
from .nodes import Generator, PostProcessor, PreProcessor
from .state import ProcessorState


class Processor:
    """LLM-backed sentiment processor powered by a LangGraph pipeline."""

    def __init__(
        self,
        prompt_path: str = "prompts/sentiment_analysis.txt",
        model: str = OLLAMA_MODEL,
        base_url: str = f"http://{OLLAMA_SERVER_URL}:{OLLAMA_SERVER_PORT}",
    ):
        self.prompt_text = self._load_prompt(prompt_path)
        self.llm = ChatOllama(model=model, base_url=base_url)

        # Initialize nodes
        self.preprocess_node = PreProcessor(self.prompt_text)
        self.generate_node = Generator(self.llm)
        self.postprocess_node = PostProcessor()

        self.graph = self._build_graph()

    def __call__(self, posts: List[Dict[str, Any]]) -> List[Optional[str]]:
        initial_state: ProcessorState = {
            "posts": posts,
            "sanitized_items": [],
            "messages": [],
            "llm_response": "",
            "final_result": [],
        }

        final_state = self.graph.invoke(initial_state)
        return final_state.get("final_result", [])

    def _build_graph(self):
        workflow = StateGraph(ProcessorState)

        workflow.add_node("preprocess", self.preprocess_node)
        workflow.add_node("generate", self.generate_node)
        workflow.add_node("postprocess", self.postprocess_node)

        workflow.add_edge(START, "preprocess")
        workflow.add_edge("preprocess", "generate")
        workflow.add_edge("generate", "postprocess")
        workflow.add_edge("postprocess", END)

        return workflow.compile()

    def _load_prompt(self, path: str) -> str:
        """
        Loads the prompt text from a file.
        """
        return Path(path).read_text().strip()
