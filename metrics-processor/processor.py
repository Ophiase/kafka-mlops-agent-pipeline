import json
from typing import List, Dict, Any
from constants import OLLAMA_MODEL, OLLAMA_SERVER_URL, OLLAMA_SERVER_PORT
from langchain_ollama import ChatOllama
from langchain.messages import SystemMessage, HumanMessage
from pathlib import Path
import re


class Processor:
    prompt: SystemMessage
    llm: ChatOllama

    def __init__(self,
                 prompt_path: str = "prompts/sentiment_analysis.txt",
                 model: str = OLLAMA_MODEL,
                 base_url: str = f"http://{OLLAMA_SERVER_URL}:{OLLAMA_SERVER_PORT}"):
        self.prompt = self.load_prompt(prompt_path)
        self.llm = self.build_llm(model, base_url)

    def __call__(self, posts: List[Dict[str, Any]]) -> List[str]:
        messages = self.build_messages(posts)
        print("[LLM] Invoke...")
        ai_response = self.llm.invoke(messages).content
        print("[LLM] Response received.")
        print("[LLM] Response:\n", ai_response)
        result = [ai_response]  # todo: split
        return result

    def load_prompt(self, path: str) -> SystemMessage:
        return SystemMessage(Path(path).read_text().strip())

    def build_llm(self, model: str, base_url: str) -> ChatOllama:
        return ChatOllama(model=model, base_url=base_url)

    def build_messages(self, posts: List[Dict[str, Any]]) -> List:
        posts: List[str] = [
            self.parse(post) for post in posts]
        humans = [HumanMessage(post) for post in posts]
        return [self.prompt] + humans

    def parse(self, content: Dict[str, Any]) -> List[str]:
        content: str = self.extract_post(content)
        content_cleaned = self.sanitize_post(content)
        # print("Cleaned Content:", content_cleaned)
        return content_cleaned

    def sanitize_post(self, post: str) -> str:
        # Remove HTML/XML tags and special characters, keep only alphanumerics and spaces
        cleaned = re.sub(r'<[^>]+>', '', post)  # Remove tags
        # Remove special characters
        cleaned = re.sub(r'[^A-Za-z0-9\s]', '', cleaned)
        return cleaned.strip()

    def extract_post(self, message: Dict[str, Any], limit=100) -> str:
        return message["text"][:limit]
