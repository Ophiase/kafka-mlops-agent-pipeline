from langchain_ollama.llms import OllamaLLM
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from constants import OLLAMA_SERVER_URL, OLLAMA_SERVER_PORT, OLLAMA_MODEL


class Processor:
    def __init__(self):
        model = OLLAMA_MODEL
        llm = self.build_llm(model)
        self.chain = self.build_chain(llm)

    def build_llm(self, model: str) -> OllamaLLM:
        ollama_server_url = f"{OLLAMA_SERVER_URL}:{OLLAMA_SERVER_PORT}"
        return OllamaLLM(model=model, base_url=ollama_server_url)

    def build_chain(self, llm: OllamaLLM) -> ConversationChain:
        memory = ConversationBufferMemory()
        return ConversationChain(llm=llm, memory=memory)

    def __call__(self, prompt: str, *args, **kwds):
        return self.chain.invoke(prompt)
