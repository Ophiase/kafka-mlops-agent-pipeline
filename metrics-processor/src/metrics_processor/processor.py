import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from .constants import OLLAMA_MODEL, OLLAMA_SERVER_PORT, OLLAMA_SERVER_URL


class ProcessorState(TypedDict):
    posts: List[Dict[str, Any]]
    sanitized_items: List[Dict[str, str]]
    messages: List[BaseMessage]
    llm_response: str
    final_result: List[Optional[str]]


class Processor:
    """LLM-backed sentiment processor powered by a LangGraph pipeline."""

    def __init__(self,
                 prompt_path: str = "prompts/sentiment_analysis.txt",
                 model: str = OLLAMA_MODEL,
                 base_url: str = f"http://{OLLAMA_SERVER_URL}:{OLLAMA_SERVER_PORT}"):
        self.prompt_text = self._load_prompt(prompt_path)
        self.llm = ChatOllama(model=model, base_url=base_url)
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

        workflow.add_node("preprocess", self._preprocess)
        workflow.add_node("generate", self._generate)
        workflow.add_node("postprocess", self._postprocess)

        workflow.add_edge(START, "preprocess")
        workflow.add_edge("preprocess", "generate")
        workflow.add_edge("generate", "postprocess")
        workflow.add_edge("postprocess", END)

        return workflow.compile()

    # --- Graph nodes ---

    def _preprocess(self, state: ProcessorState) -> Dict[str, Any]:
        """
        Prepares the input posts for LLM processing by sanitizing and formatting them,
        and constructing the initial messages for the LLM.

        Args:
            state: The current processor state containing the raw posts.
        Returns:
            A dictionary containing the sanitized items and the messages to be sent to the LLM.
        """
        sanitized: List[Dict[str, str]] = [self._sanitize_and_format(
            post) for post in state["posts"]]
        payload: Dict[str, List[Dict[str, str]]] = {"items": sanitized}

        messages: List[BaseMessage] = [
            SystemMessage(content=self.prompt_text),
            HumanMessage(content=json.dumps(payload)),
        ]

        return {
            "sanitized_items": sanitized,
            "messages": messages,
        }

    def _generate(self, state: ProcessorState) -> Dict[str, Any]:
        """
        Invokes the LLM with the prepared messages and retrieves the response.
        Args:
            state: The current processor state containing the messages for the LLM.
        Returns:
            A dictionary containing the LLM's response content.
        """
        print("[LLM] Invoke...")
        try:
            response = self.llm.invoke(state["messages"])
            content = str(response.content)
            print("[LLM] Response received.")
        except Exception as exc:  # pragma: no cover - defensive logging
            print(f"[LLM] Error during invocation: {exc}")
            content = ""

        if content:
            print("[LLM] Response:\n", content)

        return {"llm_response": content}

    def _postprocess(self, state: ProcessorState) -> Dict[str, Any]:
        expected = len(state["posts"])
        results = self._parse_response(state["llm_response"], expected)
        return {"final_result": results}

    # --- Helpers ---

    def _load_prompt(self, path: str) -> str:
        """
        Loads the prompt text from a file.
        """
        return Path(path).read_text().strip()

    def _sanitize_and_format(self, post: Dict[str, Any]) -> Dict[str, str]:
        """
        Sanitizes and formats a single post dictionary for LLM processing.
        Args:
            post: The raw post dictionary.
        Returns:
            A dictionary with sanitized 'id' and 'text' fields.
        """
        text = str(post.get("text", ""))[:100]
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"[^A-Za-z0-9\s]", "", text)
        return {
            "id": str(post.get("id", "")),
            "text": text.strip(),
        }

    def _parse_response(self, response: str, expected_count: int) -> List[Optional[str]]:
        """
        Parses the LLM response to extract sentiment analysis results.
        Args:
            response: The raw response string from the LLM.
            expected_count: The expected number of results based on input posts.
        Returns:
            A list of JSON strings representing sentiment analysis results, or None for failures.
        """

        if not response:
            return [None] * expected_count

        try:
            json_block = re.search(
                r"```json\s*(\[.*?\])\s*```", response, re.DOTALL)
            if json_block:
                response = json_block.group(1)
            else:
                bracketed = re.search(r"(\[.*\])", response, re.DOTALL)
                if bracketed:
                    response = bracketed.group(1)

            data = json.loads(response)

            if not isinstance(data, list):
                print(f"[Processor] Error: expected list, got {type(data)}")
                return [None] * expected_count

            if len(data) != expected_count:
                print(
                    f"[Processor] Warning: expected {expected_count}, got {len(data)}")
                return [None] * expected_count

            return [json.dumps(item) for item in data]

        except json.JSONDecodeError:
            print("[Processor] Failed to decode JSON response.")
            return [None] * expected_count
        except Exception as exc:
            print(f"[Processor] Unexpected error parsing response: {exc}")
            return [None] * expected_count
