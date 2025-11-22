import json
from typing import List, Dict, Any
from constants import OLLAMA_MODEL, OLLAMA_SERVER_URL, OLLAMA_SERVER_PORT
from langchain_ollama import ChatOllama
from langchain.messages import SystemMessage, HumanMessage
from pathlib import Path


class Processor:
    prompt: SystemMessage
    llm: ChatOllama

    def __init__(self,
                 prompt_path: str = "prompts/sentiment_analysis.txt",
                 model: str = OLLAMA_MODEL,
                 base_url: str = f"http://{OLLAMA_SERVER_URL}:{OLLAMA_SERVER_PORT}"):
        self.prompt = self.load_prompt(prompt_path)
        self.llm = self.build_llm(model, base_url)

    def __call__(self, posts: List[str]) -> List[Dict[str, Any]]:
        msgs = self.build_messages(posts)
        ai_msg = self.llm.invoke(msgs)
        return ai_msg.content
        # return self.parse(ai_msg.content)

    def load_prompt(self, path: str) -> SystemMessage:
        return SystemMessage(Path(path).read_text().strip())

    def build_llm(self, model: str, base_url: str) -> ChatOllama:
        return ChatOllama(model=model, base_url=base_url)

    def build_messages(self, posts: List[str]):
        system = self.prompt
        humans = [HumanMessage(post) for post in posts]
        return [system] + humans

    def parse(self, content: str) -> List[Dict[str, Any]]:
        return json.loads(content)
