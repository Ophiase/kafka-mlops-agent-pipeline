from typing import Any, Dict, List, Optional, TypedDict
from langchain_core.messages import BaseMessage

class ProcessorState(TypedDict):
    posts: List[Dict[str, Any]]
    sanitized_items: List[Dict[str, str]]
    messages: List[BaseMessage]
    llm_response: str
    final_result: List[Optional[str]]
