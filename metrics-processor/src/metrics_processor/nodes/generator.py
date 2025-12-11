from typing import Any, Dict

from langchain_ollama import ChatOllama

from ..state import ProcessorState


class Generator:
    """
    Node responsible for invoking the LLM.
    """

    def __init__(self, llm: ChatOllama):
        self.llm = llm

    def __call__(self, state: ProcessorState) -> Dict[str, Any]:
        """
        Invokes the LLM with the prepared messages and retrieves the response.
        """
        print("[LLM] Invoke...")
        try:
            response = self.llm.invoke(state["messages"])
            content = str(response.content)
            print("[LLM] Response received.")
        except Exception as exc:
            print(f"[LLM] Error during invocation: {exc}")
            content = ""

        if content:
            print("[LLM] Response:\n", content)

        return {"llm_response": content}
