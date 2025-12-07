import json
import re
from typing import Any, Dict, List
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from ..state import ProcessorState


class PreProcessor:
    """
    Node responsible for preparing the input posts for LLM processing.
    """

    def __init__(self, prompt_text: str):
        self.prompt_text = prompt_text

    def __call__(self, state: ProcessorState) -> Dict[str, Any]:
        """
        Sanitizes and formats posts, and constructs the initial messages for the LLM.
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

    def _sanitize_and_format(self, post: Dict[str, Any]) -> Dict[str, str]:
        """
        Sanitizes and formats a single post dictionary for LLM processing.
        """
        text = str(post.get("text", ""))[:100]
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"[^A-Za-z0-9\s]", "", text)
        return {
            "id": str(post.get("id", "")),
            "text": text.strip(),
        }
