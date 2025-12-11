from typing import Any, Dict

from ..state import ProcessorState
from ..utils.json_utils import parse_llm_response


class PostProcessor:
    """
    Node responsible for parsing the LLM response.
    """

    def __call__(self, state: ProcessorState) -> Dict[str, Any]:
        expected = len(state["posts"])
        results = parse_llm_response(state["llm_response"], expected)
        return {"final_result": results}
